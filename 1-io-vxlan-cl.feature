Feature: ioprocessing vxlan controller learning

    Scenario: two vxlan logicalport on different node
        Given create vxlan physicalnetwork "edac6346"
        and create logicalnetwork "1fd3954a" "edac6346"
        and create logicalport "d13f31a2" "1fd3954a" "76:b8:46:68:eb:ac"
        and ovs add interface "veth1" "d13f31a2" "host1" "76:b8:46:68:eb:ac"
        and create logicalport "963008a6" "1fd3954a" "be:cf:72:24:77:b0"
        and ovs add interface "veth1" "963008a6" "host2" "be:cf:72:24:77:b0"
        when create physicalport "vxlan0" "edac6346"
        then check controller learn flow
        and check two logicalport ping "host1" "veth1" "host2" "veth1"

        # all about vxlan learning match reg6
        # but there is no l2switch to set reg6
        # so flow about vxlan learning will not match
        # on controller learn mode there is no mac flow

        #and check learn "be:cf:72:24:77:b0" on "host1"
        #and check learn "76:b8:46:68:eb:ac" on "host2"

