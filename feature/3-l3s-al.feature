Feature: l3switch arp learn
    Scenario: l3switch logicalport on different node
        Given create vxlan physicalnetwork "edac6346"
        and create logicalnetwork "1fd3954a" "edac6346"
        and create subnet "236fae62","1fd3954a","172.100.101.0/24" "172.100.101.1"
        and create l3 logicalport "d13f31a2" "1fd3954a" "236fae62" "76:b8:46:68:eb:ac" "172.100.101.2"
        and ovs add l3 interface "veth1" "d13f31a2" "host1" "76:b8:46:68:eb:ac" "172.100.101.2" "172.100.101.1"

        and create logicalnetwork "27807868" "edac6346"
        and create subnet "31ce5574","27807868","172.100.102.0/24" "172.100.102.1"
        and create l3 logicalport "963008a6" "27807868" "31ce5574" "be:cf:72:24:77:b0" "172.100.102.2"
        and ovs add l3 interface "veth1" "963008a6" "host2" "be:cf:72:24:77:b0" "172.100.102.2" "172.100.102.1"

        when create router "c707aa9c"
        and create physicalport "vxlan0" "edac6346"
        and add router interface "c707aa9c" "236fae62"
        and add router interface "c707aa9c" "31ce5574"

        then check l3 prepush "76:b8:46:68:eb:ac" "172.100.101.2" on "host1"
        and check l3 prepush "be:cf:72:24:77:b0" "172.100.102.2" on "host2"
        and check l3 not prepush "be:cf:72:24:77:b0" "172.100.102.2" on "host1"
        and check l3 not prepush "76:b8:46:68:eb:ac" "172.100.101.2" on "host2"
        and check l3 logicalport ping "host1" "veth1" "172.100.101.2" "host1" "veth2" "172.100.102.2" success
        and check l3 prepush "be:cf:72:24:77:b0" "172.100.102.2" on "host1"
        and check l3 prepush "76:b8:46:68:eb:ac" "172.100.101.2" on "host2"

    Scenario: failover situation
     when restart kvdb
     then check l3 logicalport ping "host1" "veth1" "172.100.101.2" "host1" "veth2" "172.100.102.2" success
     when stop controller "host1"
     then check l3 logicalport ping "host1" "veth1" "172.100.101.2" "host1" "veth2" "172.100.102.2" success