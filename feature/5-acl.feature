Feature: acl flow

    Scenario: egress acl flow
        Given create vxlan physicalnetwork "edac6346"
        and create logicalnetwork "1fd3954a" "edac6346"
        and create logicalportwithegressacl "d13f31a2" "1fd3954a" "76:b8:46:68:eb:ac" "{"src_mac":"be:cf:72:24:77:b0","accept":True}"
        and ovs add interface "veth1" "d13f31a2" "host1" "76:b8:46:68:eb:ac"
        and create logicalport "963008a6" "1fd3954a" "be:cf:72:24:77:b0"
        and ovs add interface "veth1" "963008a6" "host2" "be:cf:72:24:77:b0"
        when create physicalport "vxlan0" "edac6346"
        then check l2 ping "host1" "veth1" "host2" "veth1" drop
    Scenario: egress acl update
        when update logicalportegressacl "d13f31a2" "{"src_mac":"be:cf:72:24:77:b0","accept":True}"
        then check two logicalport ping "host1" "veth1" "host2" "veth1"

    Scenario: egress acl delete
        then ovs remove interface "veth1" "host1"
        and ovs remove interface "veth1" "host2"
        and remove logicalport "d13f31a2"
        and remove logicalport "963008a6"
        and remove logicalnetwork "1fd3954a"
        and delete physicalport "vxlan0"
        and remove physicalnetwork "edac6346"

    Scenario:ingress acl add
        Given create vxlan physicalnetwork "adac6346"
        and create logicalnetwork "2fd3954a" "adac6346"
        and create logicalportwithingressacl "c13f31a2" "2fd3954a" "76:b8:46:68:eb:ac" "{"src_mac":"be:cf:72:24:77:b0","accept":False}"
        and ovs add interface "veth1" "c13f31a2" "host1" "76:b8:46:68:eb:ac"
        and create logicalport "863008a6" "2fd3954a" "be:cf:72:24:77:b0"
        and ovs add interface "veth1" "863008a6" "host2" "be:cf:72:24:77:b0"
        when create physicalport "vxlan0" "adac6346"
        then check l2 ping "host1" "veth1" "host2" "veth1" drop

    Scenario: ingress acl update
        when update logicalportingressacl "c13f31a2" "{"src_mac":"be:cf:72:24:77:b0","accept":True}"
        then check two logicalport ping "host1" "veth1" "host2" "veth1"

    Scenario: ingress acl delete
        then ovs remove interface "veth1" "host1"
        and ovs remove interface "veth1" "host2"
        and remove logicalport "c13f31a2"
        and remove logicalport "863008a6"
        and remove logicalnetwork "2fd3954a"
        and delete physicalport "vxlan0"
        and remove physicalnetwork "adac6346"

    Scenario:logicalnetwork acl add
        Given create vxlan physicalnetwork "adac6346"
        and create logicalnetworkwithacl "2fd3954a" "adac6346" "{"src_mac":"be:cf:72:24:77:b0","accept":False}"
        and create logicalport "c13f31a2" "2fd3954a" "76:b8:46:68:eb:ac"
        and ovs add interface "veth1" "c13f31a2" "host1" "76:b8:46:68:eb:ac"
        and create logicalport "863008a6" "2fd3954a" "be:cf:72:24:77:b0"
        and ovs add interface "veth1" "863008a6" "host2" "be:cf:72:24:77:b0"
        when create physicalport "vxlan0" "adac6346"
        then check two logicalport ping "host1" "veth1" "host2" "veth1"

    Scenario: logicalnetwork acl update
        when update logicalnetworkacl "2fd3954a" "{"src_mac":"be:cf:72:24:77:b0","accept":True}"
        then check two logicalport ping "host1" "veth1" "host2" "veth1"

    Scenario: logicalnetwork acl delete
        then ovs remove interface "veth1" "host1"
        and ovs remove interface "veth1" "host2"
        and remove logicalport "c13f31a2"
        and remove logicalport "863008a6"
        and remove logicalnetwork "2fd3954a"
        and delete physicalport "vxlan0"
        and remove physicalnetwork "adac6346"

    Scenario:subnet acl add
        Given create vxlan physicalnetwork "edac6346"
        and create logicalnetwork "1fd3954a" "edac6346"
        and create subnet "236fae62","1fd3954a","172.100.101.0/24" "172.100.101.1"
        and create l3 logicalport "d13f31a2" "1fd3954a" "236fae62" "76:b8:46:68:eb:ac" "172.100.101.2"
        and ovs add l3 interface "veth1" "d13f31a2" "host1" "76:b8:46:68:eb:ac" "172.100.101.2" "172.100.101.1"

        and create logicalnetwork "27807868" "edac6346"
        and create subnetwithacl "31ce5574","27807868","172.100.102.0/24" "172.100.102.1" "{"src_ip":"172.100.101.2","protocol":"udp","accept":False}"
        and create l3 logicalport "963008a6" "27807868" "31ce5574" "be:cf:72:24:77:b0" "172.100.102.2"
        and ovs add l3 interface "veth2" "963008a6" "host1" "be:cf:72:24:77:b0" "172.100.102.2" "172.100.102.1"

        when create router "c707aa9c"
        and create physicalport "vxlan0" "edac6346"
        and add router interface "c707aa9c" "236fae62"
        and add router interface "c707aa9c" "31ce5574"
        then check l3 ping "host1" "veth1" "172.100.101.2" "host1" "veth2" "172.100.102.2" drop

    Scenario: subnet acl update
        when update subnetacl "31ce5574" "{}"
        then check l3 logicalport ping "host1" "veth1" "172.100.101.2" "host1" "veth2" "172.100.102.2" success

    Scenario: logicalnetwork acl delete
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