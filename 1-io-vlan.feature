Feature: ioprocessing vlan
    Scenario: first logicalport ovs online
     Given create vlan physicalnetwork "edac6346"
     and create logicalnetwork "1fd3954a" "edac6346"
     and create logicalport "d13f31a2" "1fd3954a"
     when ovs add interface "veth1" "d13f31a2" "host1"
     then check first logicalport ovs online
     and ovs remove interface "veth1" "host1"
     and remove logicalport "d13f31a2"

    # status: physicalnetwork edac6346
    #         logicalnetwork  1fd3954a

    Scenario: first logicalport kvdb online
     Given ovs add interface "veth1" "d13f31a2" "host1"
     when create logicalport "d13f31a2" "1fd3954a"
     then check first logicalport ovs online
     and ovs remove interface "veth1" "host1"

    # status: logicalport d13f31a2 kvdb

    Scenario: first logicalport physicalport online
     Given create physicalport "bridge" "edac6346"
     when ovs add interface "veth1" "d13f31a2" "host1"
     then check logicalport physicalport online
     and ovs remove interface "bridge" "host1"
     and check logicalport physicalport offline
     and ovs add interface "bridge" "-" "host1"

    # status: physicalport bridge kvdb

    Scenario: two logicalport on same node
     Given create logicalport "dc19d850" "1fd3954a"
     when ovs add interface "veth2" "dc19d850" "host1"
     then check two logicalport ping "host1" "veth1" "host1" "veth2"

    # status: logicalport dc19d850

    Scenario: two logicalport on different node
     Given create logicalport "963008a6" "1fd3954a"
     when ovs add interface "veth1" "963008a6" "host2"
     then check two logicalport ping "host1" "veth1" "host2" "veth1"




