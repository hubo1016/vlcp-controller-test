#!/bin/bash -xe

docker -v
python -V
pip -V

imagename=vlcp-controller/test
tag=python27

[ "`docker images -q ${imagename}/${tag}`" == "" ] && (cd Dockerfile; docker build . -t ${imagename}:${tag} -f Dockerfile_${tag})

pip install -r requirements.txt

[ -f vlcp*.whl ] || pip download --only-binary all --no-deps vlcp

mkdir -p /var/run/netns

behave --junit -D tag=${tag}

