from behave import *
from apis import *
from utils import *

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


@then ('check first logicalport ovs online')
def check_first_logicalport_online(context):
    pass


@when ('check logicalport physicalport online')
@then ('check logicalport physicalport online')
def check_lp_port_online(context):
    pass


@then ('check logicalport physicalport offline')
def check_lp_port_offline(context):
    pass


@then ('check two logicalport ping "{host1}" "{name1}" "{host2}" "{name2}"')
def check_two_port_ping(context, host1, name1, host2, name2):
    pass

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
