from behave import *
from utils import *
from apis import *

@Given ('create logicalnetworkwithacl "{network_id}" "{physicalnetwork}" "{acl}"')
def create_logicalnetwork_with_acl(context, network_id, physicalnetwork, acl):
    c = create_logical_network_with_acl(network_id, physicalnetwork, acl)
    command = "curl -s '%s'" % c
    call_in_docker(context.host1, command)

@when('update logicalnetworkacl "{network_id}" "{acl}"')
def update_logicalnetwork_acl(context, network_id, acl):
    c = update_logical_network_acl(network_id, acl)
    command = "curl -s '%s'" % c
    call_in_docker(context.host1, command)

@Given ('create logicalportwithingressacl "{network_id}" "{logicalnetwork}" "{mac}" "{ingressacl}"')
def create_logicalport_with_ingressacl(context, network_id, logicalnetwork, mac, ingressacl):
    c = create_logical_port_with_ingressacl(network_id, logicalnetwork, ingressacl, mac_address=mac)
    command = "curl -s '%s'" % c
    call_in_docker(context.host1, command)

@Given('create logicalportwithegressacl "{network_id}" "{logicalnetwork}" "{mac}" "{egressacl}"')
def create_logicalport_with_egressacl(context, network_id, logicalnetwork, mac, egressacl):
    c = create_logical_port_with_egressacl(network_id, logicalnetwork, egressacl, mac_address=mac)
    command = "curl -g '%s'" % c
    print(command)
    call_in_docker(context.host1, command)

@when('update logicalportegressacl "{network_id}" "{egressacl}"')
def update_logicalport_egressacl(context, network_id, egressacl):
    c = update_logical_port_egressacl(network_id, egressacl)
    command = "curl -g '%s'" % c
    print(command)
    call_in_docker(context.host1, command)

@when('update logicalportingressacl "{network_id}" "{ingressacl}"')
def update_logicalport_ingressacl(context, network_id, ingressacl):
    c = update_logical_port_ingressacl(network_id, ingressacl)
    command = "curl -s '%s'" % c
    call_in_docker(context.host1, command)

@given('create subnetwithacl "{subnet_id}","{logicalnetwork}","{cidr}" "{gateway}" "{acl}"')
def add_subnet_with_acl(context, subnet_id, logicalnetwork, cidr, gateway, acl):
    c = create_subnet_withacl(subnet_id, logicalnetwork, cidr, gateway, acl)
    command = "curl -s '%s'" % c
    call_in_docker(context.host1, command)

@when('update subnetacl "{subnet_id}" "{acl}"')
def update_subnet_with_acl(context, subnet_id, acl):
    c = update_subnet_acl(subnet_id, acl)
    command = "curl -s '%s'" % c
    call_in_docker(context.host1, command)

@then('check l2 ping "{host1}" "{name1}" "{host2}" "{name2}" drop')
def check_l2_ping_fail(context, host1, name1, host2, name2):
    host_map = {"host1": context.host1, "host2": context.host2}
    # config ip address
    flag = name1[-1:]
    ns = "ns" + flag
    ipaddr = "172.168.1.2/24"
    veth = "vethns" + flag
    cmd = "ip netns exec %s ip link set %s up" % (ns, veth)
    call_in_docker(host_map[host1], cmd)
    cmd = "ip netns exec %s ip addr add %s dev %s" % (ns, ipaddr, veth)
    call_in_docker(host_map[host1], cmd)
    # config ip address
    flag = name2[-1:]
    ns = "ns" + flag
    ipaddr = "172.168.1.3/24"
    veth = "vethns" + flag
    cmd = "ip netns exec %s ip link set %s up" % (ns, veth)
    call_in_docker(host_map[host2], cmd)
    cmd = "ip netns exec %s ip addr add %s dev %s" % (ns, ipaddr, veth)
    call_in_docker(host_map[host2], cmd)
    try:
        # test ping
        cmd = "ip netns exec %s ping %s -w 10 -c 5" % (ns, "172.168.1.2")
        result = call_in_docker(host_map[host2], cmd)
        pattern = re.compile("(\d)% packet loss")
        match = pattern.search(result)
        if match:
            loss = int(match.groups()[0])
            print("loss")
            print(host_map[host2])
            print(loss)
            print("d"+loss)
            assert loss == 10
        else:
            raise AssertionError
    except Exception:
        pass
    # clear ip addr
    flag = name1[-1:]
    ns = "ns" + flag
    ipaddr = "172.168.1.2/24"
    veth = "vethns" + flag
    cmd = "ip netns exec %s ip addr del %s dev %s" % (ns, ipaddr, veth)
    call_in_docker(host_map[host1], cmd)
    # clear ip address
    flag = name2[-1:]
    ns = "ns" + flag
    ipaddr = "172.168.1.3/24"
    veth = "vethns" + flag
    cmd = "ip netns exec %s ip addr del %s dev %s" % (ns, ipaddr, veth)
    call_in_docker(host_map[host2], cmd)

@then('check l3 ping "{host1}" "{name1}" "{ip1}" "{host2}" "{name2}" "{ip2}" drop')
def check_l3_ping_drop(context, host1, name1, ip1, host2, name2, ip2):
    host_map = {"host1": context.host1, "host2": context.host2}
    flag = name1[-1:]
    ns = "ns" + flag
    # test ping
    try:
        cmd = "ip netns exec %s ping %s -w 10 -c 5" % (ns, ip2)
        result = call_in_docker(host_map[host1], cmd)
        pattern = re.compile("(\d)% packet loss")
        match = pattern.search(result)
        if match:
            loss = int(match.groups()[0])
            assert loss < 10
        else:
            raise AssertionError
    except Exception:
        pass


