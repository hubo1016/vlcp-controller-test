Feature: ioprocessing vxlan prepush
    Scenario: the physicalport online
        Given create vxlan physicalnetwork "edac6346"
        and create logicalnetwork "1fd3954a" "edac6346"
        and create logicalport "d13f31a2" "1fd3954a" "76:b8:46:68:eb:ac"
        and ovs add interface "veth1" "d13f31a2" "host1" "76:b8:46:68:eb:ac"
        when create physicalport "vxlan0" "edac6346"
        then check vxlan physicalport online

    Scenario: the physicalport offline
        Given delete physicalport "vxlan0"
        then check vxlan physicalport offline
        and create physicalport "vxlan0" "edac6346"


    Scenario: two vxlan logicalport on different node
        Given create logicalport "963008a6" "1fd3954a" "be:cf:72:24:77:b0"
        when ovs add interface "veth1" "963008a6" "host2" "be:cf:72:24:77:b0"
        then check prepush "be:cf:72:24:77:b0" on "host1"
        and check two logicalport ping "host1" "veth1" "host2" "veth1"