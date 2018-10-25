FROM {{base}}

# update source , install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
                              wget \
                              uuid-runtime \
                              kmod \
                              curl \
                              iproute2 \
                              iputils-ping \
                              isc-dhcp-client \
                   && rm -rf /var/lib/apt/lists/*


# install openvswitch
# RUN wget -q http://openvswitch.org/releases/openvswitch-{{ovs_version}}.tar.gz && \
#                           tar zxf openvswitch-{{ovs_version}}.tar.gz && \
#                           cd openvswitch-{{ovs_version}} && \
#                           ./configure && make && make install

COPY *.deb /root/


RUN dpkg -i /root/*.deb


# install pip and requirement
RUN if [ ! -e /usr/local/bin/pip2 ]; then : \
         && wget  --no-check-certificate -O /tmp/get-pip.py 'https://bootstrap.pypa.io/get-pip.py' \
         && python2 /tmp/get-pip.py \
         && pip2 install supervisor \
         && ln -sf $(which pip3) /opt/pip \
         && pip3 install coverage \
         && rm /tmp/get-pip.py \
    ; else \
         pip install coverage \
         && pip install supervisor \
         && ln -sf $(which pip2) /opt/pip \
    ; fi

RUN ([ -e /usr/local/bin/pypy ] && ln -sf $(which pypy) /opt/python && ln -sf $(which coverage) /opt/coverage) || \
    ([ -e /usr/local/bin/pypy3 ] && ln -sf $(which pypy3) /opt/python && ln -sf $(which coverage) /opt/coverage) || \
    (ln -sf $(which python) /opt/python && ln -sf $(which coverage) /opt/coverage)


CMD ["/bin/bash"]



