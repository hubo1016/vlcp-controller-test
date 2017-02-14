FROM {{base}}

# update source , install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
                              wget \
                              uuid-runtime \
                              curl \
                              iproute2 \
                              iputils-ping \
                   && rm -rf /var/lib/apt/lists/* 


# install openvswitch
RUN wget -q http://openvswitch.org/releases/openvswitch-{{ovs_version}}.tar.gz && \
                           tar zxf openvswitch-{{ovs_version}}.tar.gz && \
                           cd openvswitch-{{ovs_version}} && \
                           ./configure && make && make install


# install pip
RUN if [ ! -e /usr/local/bin/pip ]; then : \
         && wget  --no-check-certificate -O /tmp/get-pip.py 'https://bootstrap.pypa.io/get-pip.py' \
         && python /tmp/get-pip.py \
         && rm /tmp/get-pip.py \
    ; fi  

# pip install requirement
RUN pip install coverage && pip install supervisor

# link python interpreter to same 
RUN ln -sf $(which python) /opt/python && ln -sf $(which pip) /opt/pip\
                                          && ln -sf $(which coverage) /opt/coverage
    
CMD ["/bin/bash"]



