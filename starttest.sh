#!/bin/bash -xe

docker -v
python -V
pip -V

imagename=vlcp-controller/test

tag=$1
kvdb=$2
coverage=$3


if [ "$tag" == "" ]; then
    tag=python2.7
fi

if [ "$kvdb" == "" ]; then
    kvdb=redis
fi

base=python:2.7

if [ "${tag:0:6}" == "python" ]; then
     base=python:${tag:6}
elif [ "${tag:0:4}" == "pypy" ]; then
     # only support pypy 2
     base=pypy:2-5
fi

pip install -r requirements.txt

[ "`docker images -q ${imagename}:${tag}`" == "" ] && (cd Dockerfile; python build-image.py ${base} -name ${imagename} -tag $tag)

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


