from behave import *
from apis import *
from utils import *

import re



@Given ('create vlan physicalnetwork "{network_id}"')
def create_vlan_physicalnetwork(context, network_id):

    c = create_physical_network(network_id)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)



@Given ('create logicalnetwork "{network_id}" "{physicalnetwork}"')
def create_logicalnetwork(context,network_id, physicalnetwork):

    c = create_logical_network(network_id, physicalnetwork)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@when ('create logicalport "{network_id}" "{logicalnetwork}" "{mac}"')
@Given ('create logicalport "{network_id}" "{logicalnetwork}" "{mac}"')
def create_logicalport(context, network_id, logicalnetwork, mac):

    c = create_logical_port(network_id, logicalnetwork, mac_address=mac)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@then ('remove logicalport "{network_id}"')
def remove_logicalport(context, network_id):

    c = remove_logical_port(network_id)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@given ('ovs add interface "{vethname}" "{ifaceid}" "{host}" "{mac}"')
@when ('ovs add interface "{vethname}" "{ifaceid}" "{host}" "{mac}"')
@then ('ovs add interface "{vethname}" "{ifaceid}" "{host}" "{mac}"')
def ovs_add_interface(context, vethname, ifaceid, host, mac):
    
    host_map = {"host1": context.host1, "host2": context.host2}
    if vethname == "bridge":
        # bridge interface have been create , so only add it to ovs
        cmd = "ovs-vsctl add-port br0 %s -- set interface %s external_ids:vtep-physname=br0 " \
              "external_ids:vtep-phyiname=%s" % (vethname,vethname,"docker-" + host_map[host][0:4])
        call_in_docker(host_map[host], cmd)
        return
    
    # vethname eg veth1
    flag = vethname[-1:]

    ns = "ns%s" % flag
    
    cmd = "ip netns add %s" % ns
    call_in_docker(host_map[host], cmd)

    cmd = "ip link add %s type veth peer name %s" % (vethname, "vethns"+flag)
    call_in_docker(host_map[host], cmd)

    cmd = "ip link set %s up" % vethname
    call_in_docker(host_map[host], cmd)

    cmd = "ip link set %s netns %s" % ("vethns"+flag, ns)
    call_in_docker(host_map[host], cmd)

    if mac:
        cmd = "ip netns exec %s ip link set %s address %s" % (ns, "vethns"+flag, mac)
        call_in_docker(host_map[host], cmd)

    cmd = "ovs-vsctl add-port br0 %s  -- set interface %s external_ids:iface-id=%s" % (vethname,vethname,ifaceid)

    call_in_docker(host_map[host], cmd)


@then ('check first logicalport ovs online "{host}"')
def check_first_logicalport_online(context, host):

    host_map = {"host1": context.host1, "host2": context.host2}
    flow_map = {"host1": context.host1_flow_map, "host2": context.host2_flow_map}

    flow = flow_map[host]
    # table ingress  flow number > 1
    assert "ingress" in flow
    ingress = flow["ingress"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | wc -l " % ingress

    result = check_flow_table(host_map[host], cmd)
    assert int(result) > 1

    # table egress  have IN_PORT
    assert "egress" in flow
    egress = flow["egress"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep 'IN_PORT' | wc -l" % egress
    result = check_flow_table(host_map[host], cmd)
    assert int(result) >= 1



@when ('check logicalport physicalport online "{host}"')
@then ('check logicalport physicalport online "{host}"')
def check_lp_port_online(context, host):
    host_map = {"host1": context.host1, "host2": context.host2}
    flow_map = {"host1": context.host1_flow_map, "host2": context.host2_flow_map}

    flow = flow_map[host]
    # table ingress  flow number > 2
    assert "ingress" in flow
    ingress = flow["ingress"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | wc -l" % ingress
    result = check_flow_table(host_map[host], cmd)
    assert int(result) > 2

    # table egress have push_vlan:0x8100
    assert "egress" in flow
    egress = flow["egress"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep 'push_vlan:0x8100' | wc -l" % egress
    result = check_flow_table(host_map[host], cmd)
    assert int(result) >= 1

@then ('check logicalport physicalport offline "{host}"')
def check_lp_port_offline(context, host):
    host_map = {"host1": context.host1, "host2": context.host2}
    flow_map = {"host1": context.host1_flow_map, "host2": context.host2_flow_map}

    flow = flow_map[host]
    # table egress flow number = 2
    assert "ingress" in flow
    ingress = flow["ingress"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | wc -l " % ingress
    result = check_flow_table(host_map[host], cmd)
    assert int(result) <= 3

    # table egress have push_vlan:0x8100
    assert "egress" in flow
    egress = flow["egress"]

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep 'push_vlan:0x8100' | wc -l" % egress
    result = check_flow_table(host_map[host], cmd)
    assert int(result) <= 0


@then ('check two logicalport ping "{host1}" "{name1}" "{host2}" "{name2}"')
def check_two_port_ping(context, host1, name1, host2, name2):
    host_map = {"host1": context.host1, "host2": context.host2}

    # config ip address
    flag = name1[-1:]
    ns = "ns" + flag
    ipaddr = "172.168.1.2/24"
    veth = "vethns" + flag
    cmd = "ip netns exec %s ip link set %s up" % (ns,veth)
    call_in_docker(host_map[host1],cmd)
    cmd = "ip netns exec %s ip addr add %s dev %s" % (ns,ipaddr,veth)
    call_in_docker(host_map[host1],cmd)

    # config ip address
    flag = name2[-1:]
    ns = "ns" + flag
    ipaddr = "172.168.1.3/24"
    veth = "vethns" + flag
    cmd = "ip netns exec %s ip link set %s up" % (ns,veth)
    call_in_docker(host_map[host2],cmd)
    cmd = "ip netns exec %s ip addr add %s dev %s" % (ns,ipaddr,veth)
    call_in_docker(host_map[host2],cmd)

    # test ping
    cmd = "ip netns exec %s ping %s -w 10 -c 5" % (ns,"172.168.1.2")
    result = call_in_docker(host_map[host2],cmd)

    pattern = re.compile("(\d)% packet loss")

    match = pattern.search(result)
    assert match is not None

    if match:
        loss = int(match.groups()[0])
        assert loss <= 10

    # clear ip addr
    flag = name1[-1:]
    ns = "ns" + flag
    ipaddr = "172.168.1.2/24"
    veth = "vethns" + flag
    cmd = "ip netns exec %s ip addr del %s dev %s" % (ns,ipaddr,veth)
    call_in_docker(host_map[host1],cmd)

    # clear ip address
    flag = name2[-1:]
    ns = "ns" + flag
    ipaddr = "172.168.1.3/24"
    veth = "vethns" + flag
    cmd = "ip netns exec %s ip addr del %s dev %s" % (ns,ipaddr,veth)
    call_in_docker(host_map[host2],cmd)


@given ('ovs remove interface "{vethname}" "{host}"')
@when ('ovs remove interface "{vethname}" "{host}"')
@then ('ovs remove interface "{vethname}" "{host}"')
def ovs_remove_interface(context, vethname, host):
    host_map = {"host1": context.host1, "host2": context.host2}

    cmd = "ovs-vsctl del-port %s" % vethname
    
    call_in_docker(host_map[host], cmd)
    
    if vethname != "bridge": 
        # delete namespace ,  veth link will delete auto 
        cmd = "ip netns del %s" % "ns" + vethname[-1:]
    
        call_in_docker(host_map[host], cmd)

@when ('create physicalport "{name}" "{physicalnetwork}"')
@Given ('create physicalport "{name}" "{physicalnetwork}"')
@then ('create physicalport "{name}" "{physicalnetwork}"')
def create_physicalport(context, name, physicalnetwork):

    c = create_physical_port(name, physicalnetwork)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@when('create special physicalport "{name}" on "{host}" "{physicalnetwork}"')
def create_special_physicalport(context, name, host, physicalnetwork):

    host_map = {"host1": context.host1, "host2": context.host2}

    url = 'http://127.0.0.1:8081/ovsdbmanager/getsystemids'
    cmd = 'curl -s "%s"' % url

    result = call_in_docker(host_map[host], cmd)

    msg = json.loads(result)
    systemid= msg['result'][0]

    c = create_physical_port(name, physicalnetwork, systemid=systemid)
    command = "curl -s '%s'" % c

    call_in_docker(host_map[host], command)
