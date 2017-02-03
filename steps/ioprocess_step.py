from behave import *
from apis import *
from utils import *

import re
import time


@Given ('create vlan physicalnetwork "{network_id}"')
def create_vlan_physicalnetwork(context, network_id):

    c = create_physical_network(network_id)

    command = 'python -c "%s"' % c

    call_in_docker(context.host1, command)



@Given ('create logicalnetwork "{network_id}" "{physicalnetwork}"')
def create_logicalnetwork(context,network_id, physicalnetwork):

    c = create_logical_network(network_id, physicalnetwork)

    command = 'python -c "%s"' % c

    call_in_docker(context.host1, command)



@when ('create logicalport "{network_id}" "{logicalnetwork}"')
@Given ('create logicalport "{network_id}" "{logicalnetwork}"')
def create_logicalport(context, network_id, logicalnetwork):

    c = create_logical_port(network_id, logicalnetwork)

    command = 'python -c "%s"' % c

    call_in_docker(context.host1, command)


@then ('remove logicalport "{network_id}"')
def remove_logicalport(context, network_id):

    c = remove_logical_port(network_id)

    command = 'python -c "%s"' % c

    call_in_docker(context.host1, command)


@given ('ovs add interface "{vethname}" "{ifaceid}" "{host}"')
@when ('ovs add interface "{vethname}" "{ifaceid}" "{host}"')
@then ('ovs add interface "{vethname}" "{ifaceid}" "{host}"')
def ovs_add_interface(context, vethname, ifaceid, host):
    
    host_map = {"host1": context.host1, "host2": context.host2}
    if vethname == "bridge":
        # bridge interface have been create , so only add it to ovs
        cmd = "ovs-vsctl add-port br0 %s" % vethname
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

    cmd = "ovs-vsctl add-port br0 %s  -- set interface %s external_ids:iface-id=%s" % (vethname,vethname,ifaceid)

    call_in_docker(host_map[host], cmd)


@then ('check first logicalport ovs online "{host}"')
def check_first_logicalport_online(context, host):

    host_map = {"host1": context.host1, "host2": context.host2}

    # table 0  flow number > 1
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=0' | wc -l "
    result = call_in_docker(host_map[host], cmd)
    assert int(result) > 1

    # table 7  have IN_PORT
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=7' | grep 'IN_PORT' | wc -l"
    resutl = call_in_docker(host_map[host], cmd)
    assert int(result) >= 1



@when ('check logicalport physicalport online "{host}"')
@then ('check logicalport physicalport online "{host}"')
def check_lp_port_online(context, host):
    host_map = {"host1": context.host1, "host2": context.host2}

    time.sleep(5)

    # table 0 flow number > 2
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=0' | wc -l"
    result = call_in_docker(host_map[host], cmd)
    assert int(result) > 2

    # table 7 have push_vlan:0x8100
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=7' | grep 'push_vlan:0x8100' | wc -l"
    result = call_in_docker(host_map[host], cmd)
    assert int(result) >= 1

@then ('check logicalport physicalport offline "{host}"')
def check_lp_port_offline(context, host):
    host_map = {"host1": context.host1, "host2": context.host2}

    # table 0 flow number = 2
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=0' | wc -l "
    result = call_in_docker(host_map[host], cmd)
    assert int(result) <= 3

    # table 7 have push_vlan:0x8100
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=7' | grep 'push_vlan:0x8100' | wc -l"
    result = call_in_docker(host_map[host], cmd)
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

@Given ('create physicalport "{name}" "{physicalnetwork}"')
def create_physicalport(context, name, physicalnetwork):

    c = create_physical_port(name, physicalnetwork)

    command = 'python -c "%s"' % c

    call_in_docker(context.host1, command)
