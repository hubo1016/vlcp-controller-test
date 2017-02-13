#!/bin/bash -xe

docker -v
python -V
pip -V

imagename=vlcp-controller/test
tag=$1

if [ "${tag}" == "python2.7" ]; then
    tag="python27"
fi

if [ "${tag:0:7}" == "python3" ]; then
    tag="python3"
fi

[ "`docker images -q ${imagename}/${tag}`" == "" ] && (cd Dockerfile; docker build . -t ${imagename}:${tag} -f Dockerfile_${tag})

pip install -r requirements.txt

[ -f vlcp*.whl ] || pip download --only-binary all --no-deps vlcp

mkdir -p /var/run/netns

modprobe openvswitch

behave --junit -D tag=${tag}

