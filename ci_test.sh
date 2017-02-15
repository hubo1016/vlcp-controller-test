#!/bin/bash -xe

[ -f "/home/travis/virtualenv/${venv}/bin/activate" ] && source /home/travis/virtualenv/${venv}/bin/activate

python --version

venv=python2.7

if [ "${TRAVIS_PYTHON_VERSION}" == "pypy" ]; then
	venv=pypy2
else
	venv=python${TRAVIS_PYTHON_VERSION}
fi

bash -xe starttest.sh $venv
