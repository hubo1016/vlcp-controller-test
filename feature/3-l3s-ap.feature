Feature: l3switch arp prepush
    Scenario: l3switch logicalport on same node
        Given create vxlan physicalnetwork "edac6346"
        and create logicalnetwork "1fd3954a" "edac6346"
        and create subnet "236fae62","1fd3954a","172.100.101.0/24" "172.100.101.1"
        and create l3 logicalport "d13f31a2" "1fd3954a" "236fae62" "76:b8:46:68:eb:ac" "172.100.101.2"
        and ovs add l3 interface "veth1" "d13f31a2" "host1" "76:b8:46:68:eb:ac" "172.100.101.2" "172.100.101.1"

        and create logicalnetwork "27807868" "edac6346"
        and create subnet "31ce5574","27807868","172.100.102.0/24" "172.100.102.1"
        and create l3 logicalport "963008a6" "27807868" "31ce5574" "be:cf:72:24:77:b0" "172.100.102.2"
        and ovs add l3 interface "veth2" "963008a6" "host1" "be:cf:72:24:77:b0" "172.100.102.2" "172.100.102.1"

        when create router "c707aa9c"
        and create physicalport "vxlan0" "edac6346"
        and add router interface "c707aa9c" "236fae62"
        and add router interface "c707aa9c" "31ce5574"

        then check l3 prepush "76:b8:46:68:eb:ac" "172.100.101.2" on "host1"
        and check l3 prepush "be:cf:72:24:77:b0" "172.100.102.2" on "host1"
        and check l3 logicalport ping "host1" "veth1" "172.100.101.2" "host1" "veth2" "172.100.102.2" success
        and remove router interface "c707aa9c" "31ce5574"
        then check l3 logicalport ping "host1" "veth1" "172.100.101.2" "host1" "veth2" "172.100.102.2" fail


    Scenario: l3switch logicalport on different node
        Given add router interface "c707aa9c" "31ce5574"
        and ovs remove interface "veth2" "host1"
        when ovs add l3 interface "veth1" "963008a6" "host2" "be:cf:72:24:77:b0" "172.100.102.2" "172.100.102.1"

        then check l3 prepush "be:cf:72:24:77:b0" "172.100.102.2" on "host1"
        and check l3 prepush "76:b8:46:68:eb:ac" "172.100.101.2" on "host2"
        and check l3 logicalport ping "host1" "veth1" "172.100.101.2" "host2" "veth1" "172.100.102.2" success

    Scenario: api update test
        Given update logicalport name "d13f31a2" "test_logicalport"
        and update logicalnetwork name "1fd3954a" "test_logicalnetwork"
        and update physicalnetwork name "edac6346" "test_physicalnetwork"
        and update physicalport "vxlan0" test "test"
        and update subnet name "236fae62" "test_physicalnetwork"
        and update router name "c707aa9c" "test_router"
        and update subnet gateway "236fae62" "172.100.101.254"
        then check logicalport name "d13f31a2" "test_logicalport"
        and check logicalnetwork name "1fd3954a" "test_logicalnetwork"
        and check physicalnetwork name "edac6346" "test_physicalnetwork"
        and check physicalport "vxlan0" test "test"
        and check subnet name "236fae62" "test_physicalnetwork"
        and check router name "c707aa9c" "test_router"
        and check l3 logicalport ping "host1" "veth1" "172.100.101.2" "host2" "veth1" "172.100.102.2" success

    Scenario: api delete test
        then remove logicalport "963008a6"
        and remove logicalport "d13f31a2"
        and remove router interface "c707aa9c" "31ce5574"
        and remove router interface "c707aa9c" "236fae62"
        and remove subnet "31ce5574"
        and remove subnet "236fae62"
        and remvoe router "c707aa9c"
        and remove logicalnetwork "1fd3954a"
        and remove logicalnetwork "27807868"
        and delete physicalport "vxlan0"
        and remove physicalnetwork "edac6346"

    Scenario: unload module
        given unload module "random"
        then check unload module success
