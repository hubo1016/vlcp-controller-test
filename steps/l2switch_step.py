from behave import *
from utils import *


@then('check l2switch prepush "{mac}" on "{host}"')
def check_l2switch_prepush(context, mac, host):
    host_map = {"host1": context.host1, "host2": context.host2}

    # on l2output flow will have mac flow
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=4' | grep %s | wc -l" % mac

    result = call_in_docker(host_map[host], cmd)

    assert int(result) >= 1


@then("check l2switch flow learn flow")
def check_l2switch_flow_learn(context):

    # table 1 have mac learn flow
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=1' | grep 'learn' | wc -l"

    result = call_in_docker(context.host1, cmd)

    assert int(result) >= 1


@then("check l2switch controller learn flow")
def check_l2switch_controller_learn(context):
    # table 1 have mac learn flow
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=1' | grep 'CONTROLLER' | wc -l"

    result = call_in_docker(context.host1, cmd)

    assert int(result) >= 1


@then('check l2switch learn "{mac}" on "{host}"')
def check_l2switch_learn(context, mac, host):
    host_map = {"host1": context.host1, "host2": context.host2}

    # on l2learning flow will have mac flow
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=7' | grep %s | wc -l" % mac

    result = call_in_docker(host_map[host], cmd)

    assert int(result) >= 1


@then('check l2switch controller learn "{mac}" on "{host}"')
def check_l2switch_learn(context, mac, host):
    host_map = {"host1": context.host1, "host2": context.host2}

    # on l2learning flow will have mac flow
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=4' | grep %s | wc -l" % mac

    result = call_in_docker(host_map[host], cmd)

    assert int(result) >= 1