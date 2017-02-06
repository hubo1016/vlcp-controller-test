#!/bin/bash

imagename=vlcp-controller/test
tag=python2.7

[ "`docker images -q ${imagename}/${tag}`" == "" ] && (cd Dockerfile; docker build . -t ${imagename}/${tag})
pip install -r requirements.txt

behave --junit -D tag=${tag}
