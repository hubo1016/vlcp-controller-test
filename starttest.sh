#!/bin/bash -xe

docker -v
python -V
pip -V

imagename=vlcp-controller/test

tag=$1
kvdb=$2
coverage=$3
cache_dir=$4
ovs_version=$5



if [ "$tag" == "" ]; then
    tag=python2.7
fi

if [ "$kvdb" == "" ]; then
    kvdb=redis
fi

if [ "$ovs_version" == "" ]; then
    ovs_version=2.5.1
fi

if [ "$cache_dir" == "" ]; then
    cache_dir=`pwd`/cache
fi

base=python:2.7

if [ "${tag:0:6}" == "python" ]; then
    t=${tag:6}
    if [[ "$t" == *-dev ]]; then
        t=${t%-dev}-rc
    fi
    base=python:${t}
elif [ "${tag:0:5}" == "pypy3" ]; then
    base=pypy:3
elif [ "${tag:0:4}" == "pypy" ]; then
    base=pypy:2
fi

pip install -r requirements.txt

# [ "`docker images -q ${imagename}:${tag}`" == "" ] && (cd Dockerfile; python build-image.py ${base} -name ${imagename} -tag $tag)

if [ "`docker images -q ${imagename}:${tag}`" == "" ]; then
    # controller test image not existed , build the image first
    ovs_lib_deb=libopenvswitch_${ovs_version}-1_amd64.deb
    ovs_common_deb=openvswitch-common_${ovs_version}-1_amd64.deb
    ovs_switch_deb=openvswitch-switch_${ovs_version}-1_amd64.deb
    ovs_vtep_deb=openvswitch-vtep_${ovs_version}-1_amd64.deb
    ovs_python_deb=python-openvswitch_${ovs_version}-1_all.deb
    ovs_package=openvswitch-${ovs_version}.tar.gz
    
    # build ovs deb and store deb to cache dir
    if [ ! -e "${cache_dir}/${ovs_common_deb}" ] || [ ! -e "$cache_dir/${ovs_switch_deb}" ] || [ ! -e "$cache_dir"/${ovs_vtep_deb} ] || [ ! -e "$cache_dir"/${ovs_python_deb} ] || [ ! -e "$cache_dir"/${ovs_package} ]; then
        chmod +x Dockerfile/build_ovs.sh
        tmp_file=`cat /proc/sys/kernel/random/uuid`
        docker run -it -v ${cache_dir}:${cache_dir} -v `pwd`/Dockerfile:/tmp/$tmp_file -e "CACHE_DIR=${cache_dir}" $base /tmp/$tmp_file/build_ovs.sh "${ovs_version}"
    fi
    
    # copy ovs tar to build docker context
    # deb build not have python lib , so we cache ovs package source
    # install ovs python lib from ovs package source
    [ ! -e "Dockerfile/${ovs_package}" ] && ( cp ${cache_dir}/${ovs_package} Dockerfile)
    
    # copy ovs deb to build docker context
    [ ! -e "Dockerfile/${ovs_lib_deb}" && -e ${cache_dir}/${ovs_lib_deb} ] && ( cp ${cache_dir}/${ovs_lib_deb} Dockerfile)
    [ ! -e "Dockerfile/${ovs_common_deb}" ] && ( cp ${cache_dir}/${ovs_common_deb} Dockerfile)
    [ ! -e "Dockerfile/${ovs_switch_deb}" ] && ( cp ${cache_dir}/${ovs_switch_deb} Dockerfile)
    [ ! -e "Dockerfile/${ovs_vtep_deb}" ] && ( cp ${cache_dir}/${ovs_vtep_deb} Dockerfile)
    [ ! -e "Dockerfile/${ovs_python_deb}" ] && ( cp ${cache_dir}/${ovs_python_deb} Dockerfile)
    
    (cd Dockerfile; python build-image.py ${base} -name ${imagename} -ovs_version ${ovs_version} -tag $tag)
fi


[ -f vlcp*.whl ] || pip download --only-binary all --no-deps vlcp

mkdir -p /var/run/netns

modprobe openvswitch

if [ "$coverage" == "" ]; then
    echo behave --junit -D tag=${tag} -D db=${kvdb} feature
    behave --junit -D tag=${tag} -D db=${kvdb} feature
else
    echo behave --junit -D tag=${tag} -D coverage=true -D db=${kvdb} feature
    behave --junit -D tag=${tag} -D coverage=true -D db=${kvdb} feature
fi


