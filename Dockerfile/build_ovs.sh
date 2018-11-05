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

# Apply patch to workaround a packaging bug
(cd openvswitch-${ovs_version} && patch -p1 < ../ovs_package.patch)

(cd openvswitch-${ovs_version}; DEB_BUILD_OPTIONS='parallel=8 nocheck' fakeroot debian/rules binary)

cp *.deb $cache_dir

rm -rf openvswitch-${ovs_version}.tar.gz openvswitch-${ovs_version} *.deb
