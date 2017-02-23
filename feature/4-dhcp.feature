Feature: dhcp client
    Scenario: dhcp get ip for host
        Given create vxlan physicalnetwork "edac6346"
        and create logicalnetwork "1fd3954a" "edac6346"
        and create subnet "236fae62","1fd3954a","172.100.101.0/24" "172.100.101.1"
        and create l3 logicalport "d13f31a2" "1fd3954a" "236fae62" "76:b8:46:68:eb:ac" "172.100.101.2"
        when ovs add interface "veth1" "d13f31a2" "host1" "76:b8:46:68:eb:ac"
        and dhcp get ip "host1" "veth1"
        then check get ip "host1" "veth1" "172.100.101.2"


