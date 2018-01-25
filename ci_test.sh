#!/bin/bash -xe

venv=python2.7

if [ "${TRAVIS_PYTHON_VERSION}" == "pypy-5.4" ]; then
	venv=pypy-5.4
else
	venv=python${TRAVIS_PYTHON_VERSION}
fi

[ -f "/home/travis/virtualenv/${venv}/bin/activate" ] && source /home/travis/virtualenv/${venv}/bin/activate

python --version

bash -xe starttest.sh $venv redis coverage 
