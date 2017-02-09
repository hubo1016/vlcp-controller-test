from behave import *
from apis import *
from utils import *


@then('check l2switch prepush "{mac}" on "{host}"')
def check_l2switch_prepush(context, mac, host):
    host_map = {"host1": context.host1, "host2": context.host2}

    # on l2output flow will have mac flow
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=4' | grep %s | wc -l" % mac

    result = check_flow_table(host_map[host], cmd)

    assert int(result) >= 1


@then("check l2switch flow learn flow")
def check_l2switch_flow_learn(context):

    # table l2input have mac learn flow
    assert "l2input" in context.host1_flow_map
    l2input = context.host1_flow_map["l2input"]
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep 'learn' | wc -l" % l2input

    result = check_flow_table(context.host1, cmd)

    assert int(result) >= 1


@then("check l2switch controller learn flow")
def check_l2switch_controller_learn(context):
    # table l2input have mac learn flow
    assert "l2input" in context.host1_flow_map
    l2input = context.host1_flow_map["l2input"]
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep 'CONTROLLER' | wc -l" % l2input

    result = check_flow_table(context.host1, cmd)

    assert int(result) >= 1


@then('check l2switch learn "{mac}" on "{host}"')
def check_l2switch_learn(context, mac, host):
    host_map = {"host1": context.host1, "host2": context.host2}
    flow_map = {"host1": context.host1_flow_map, "host2": context.host2_flow_map}

    flow = flow_map[host]
    # on l2learning flow will have mac flow
    assert "l2learning" in flow
    l2learning = flow["l2learning"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep %s | wc -l" % (l2learning, mac)

    result = check_flow_table(host_map[host], cmd)

    assert int(result) >= 1


@then('check l2switch controller learn "{mac}" on "{host}"')
def check_l2switch_learn(context, mac, host):
    host_map = {"host1": context.host1, "host2": context.host2}
    flow_map = {"host1": context.host1_flow_map, "host2": context.host2_flow_map}

    flow = flow_map[host]
    # on l2output flow will have mac flow
    assert "l2output" in flow
    l2output = flow["l2output"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep %s | wc -l" % (l2output,mac)

    result = check_flow_table(host_map[host], cmd)

    assert int(result) >= 1