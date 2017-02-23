from behave import *
from utils import *
from apis import *


@Given('create vxlan physicalnetwork "{network_id}"')
def create_vxlan_physicalnetwork(context, network_id):
    c = create_physical_network(network_id, type="vxlan")

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@Given ('delete physicalport "{name}"')
@then ('delete physicalport "{name}"')
def delete_physical_port(context, name):
    c = remove_physical_port(name)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@then("check vxlan physicalport online")
def check_vxlan_physicalport_online(context):
    # table egress have tun_id flow > 0
    assert "ingress" in context.host1_flow_map
    ingress = context.host1_flow_map["ingress"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep 'tun_id=' | wc -l" % ingress

    result = check_flow_table(context.host1, cmd)

    assert int(result) >= 1


@Then("check vxlan physicalport offline")
def check_vxlan_physicalport_offline(context):

    # table egress have tun_id flow < 1
    assert "ingress" in context.host1_flow_map
    ingress = context.host1_flow_map["ingress"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep 'tun_id=' | wc -l" % ingress

    result = check_flow_table(context.host1, cmd)

    assert int(result) <= 0


@Then('check prepush "{mac}" on "{host}"')
def check_vxlan_prepush(context, mac, host):
    host_map = {"host1": context.host1, "host2": context.host2}
    flow_map = {"host1": context.host1_flow_map, "host2": context.host2_flow_map}

    flow = flow_map[host]
    # vxlanoutput table should have prepush flow
    assert "vxlanoutput" in flow
    vxlanoutput = flow["vxlanoutput"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep %s | wc -l" % (vxlanoutput,mac)

    result = check_flow_table(host_map[host], cmd)

    assert int(result) >= 1

@then("check flow learn flow")
def check_flow_learn_flow(context):

    # table vxlaninput have learn flow command
    assert "vxlaninput" in context.host1_flow_map
    vxlaninput = context.host1_flow_map["vxlaninput"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep 'learn'| wc -l" % vxlaninput
    result = check_flow_table(context.host1, cmd)

    assert int(result) >= 1


@then("check controller learn flow")
def check_controller_learn_flow(context):

    # table vxlaninput have learn controller command
    assert "vxlanoutput" in context.host1_flow_map
    vxlanoutput = context.host1_flow_map["vxlanoutput"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep 'CONTROLLER'| wc -l" % vxlanoutput
    result = check_flow_table(context.host1, cmd)

    assert int(result) >= 1


@then('check learn "{mac}" on "{host}"')
def check_vxlan_learn(context, mac, host):

    host_map = {"host1": context.host1, "host2": context.host2}
    flow_map = {"host1": context.host1_flow_map, "host2": context.host2_flow_map}

    flow = flow_map[host]
    # vxlanlearning table should have prepush flow
    assert "vxlanlearning" in flow
    vxlanlearning = flow["vxlanlearning"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep %s | wc -l" % (vxlanlearning,mac)

    result = check_flow_table(host_map[host], cmd)

    assert int(result) >= 1


