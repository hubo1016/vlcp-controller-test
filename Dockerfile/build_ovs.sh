#!/bin/bash

set -xe

env

ovs_version=$1
cache_dir=${CACHE_DIR}

wget -q http://openvswitch.org/releases/openvswitch-${ovs_version}.tar.gz

tar zxf openvswitch-${ovs_version}.tar.gz

apt-get update

apt-get install -y build-essential fakeroot

apt-get install -y graphviz autoconf automake bzip2 debhelper dh-autoreconf libssl-dev libtool openssl procps python-all python-qt4 python-twisted-conch python-zopeinterface python-six uuid-runtime

(cd openvswitch-${ovs_version}; DEB_BUILD_OPTIONS='parallel=8 nocheck' fakeroot debian/rules binary)

cp *.deb $cache_dir
cp openvswitch-${ovs_version}.tar.gz $cache_dir

