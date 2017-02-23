from behave import *
from apis import *
from utils import *

@given('create subnet "{subnet_id}","{logicalnetwork}","{cidr}" "{gateway}"')
def add_subnet(context, subnet_id, logicalnetwork, cidr, gateway):

    c = create_subnet(subnet_id, logicalnetwork, cidr, gateway)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@given('create l3 logicalport "{logicalport_id}" "{logicalnetwork}" "{subnet}" "{mac}" "{ip}"')
def create_l3_logicalport(context, logicalport_id, logicalnetwork, subnet, mac, ip):

    c = create_logical_port(id=logicalport_id, logicalnetwork=logicalnetwork, subnet=subnet,
                            mac_address=mac, ip_address=ip)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)

@given('ovs add l3 interface "{vethname}" "{ifaceid}" "{host}" "{mac}" "{ip}" "{gateway}"')
@when('ovs add l3 interface "{vethname}" "{ifaceid}" "{host}" "{mac}" "{ip}" "{gateway}"')
def ovs_add_l3_interface(context, vethname, ifaceid, host, mac, ip, gateway):
    host_map = {"host1": context.host1, "host2": context.host2}

    # vethname eg veth1
    flag = vethname[-1:]

    ns = "ns%s" % flag

    cmd = "ip netns add %s" % ns
    call_in_docker(host_map[host], cmd)

    cmd = "ip link add %s type veth peer name %s" % (vethname, "vethns" + flag)
    call_in_docker(host_map[host], cmd)

    cmd = "ip link set %s up" % vethname
    call_in_docker(host_map[host], cmd)

    cmd = "ip link set %s netns %s" % ("vethns" + flag, ns)
    call_in_docker(host_map[host], cmd)

    if mac:
        cmd = "ip netns exec %s ip link set %s address %s" % (ns, "vethns" + flag, mac)
        call_in_docker(host_map[host], cmd)

    if ip:
        cmd = "ip netns exec %s ip addr add %s dev %s" % (ns, ip + "/24", "vethns" + flag )
        call_in_docker(host_map[host], cmd)

        cmd = "ip netns exec %s ip link set dev %s up" % (ns, "vethns" + flag)
        call_in_docker(host_map[host], cmd)

    if gateway:
        cmd = "ip netns exec %s ip route add default via %s" % (ns, gateway)
        call_in_docker(host_map[host], cmd)

    cmd = "ovs-vsctl add-port br0 %s  -- set interface %s external_ids:iface-id=%s" % (vethname, vethname, ifaceid)

    call_in_docker(host_map[host], cmd)


@when('create router "{routerid}"')
def add_router(context, routerid):

    c = create_router(id=routerid)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)

@given('add router interface "{router}" "{subnet}"')
@when('add router interface "{router}" "{subnet}"')
def create_router_interface(context, router, subnet):

    c = add_router_interface(router,subnet)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@given('remove router interface "{router}" "{subnet}"')
@then('remove router interface "{router}" "{subnet}"')
def remove_router_interface(context, router, subnet):

    c = del_router_interface(router,subnet)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@then('check l3 prepush "{mac}" "{ip}" on "{host}"')
def check_l3_prepush(context, mac , ip, host):

    host_map = {"host1": context.host1, "host2": context.host2}
    flow_map = {"host1": context.host1_flow_map, "host2": context.host2_flow_map}

    flow = flow_map[host]

    assert "l3output" in flow
    l3output = flow["l3output"]
    # there is mac ip flow in table l3output
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep %s | wc -l" % (l3output, mac)

    result = check_flow_table(host_map[host], cmd)

    assert int(result) >= 1

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep %s | wc -l" % (l3output, ip)

    result = check_flow_table(host_map[host], cmd)

    assert int(result) >= 1


@then('check l3 not prepush "{mac}" "{ip}" on "{host}"')
def check_l3__no_prepush(context, mac , ip, host):

    host_map = {"host1": context.host1, "host2": context.host2}
    flow_map = {"host1": context.host1_flow_map, "host2": context.host2_flow_map}

    flow = flow_map[host]

    assert "l3output" in flow
    l3output = flow["l3output"]
    # there is no mac ip flow in table l3output
    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep %s | wc -l" % (l3output, mac)

    result = check_flow_table(host_map[host], cmd)

    assert int(result) <= 0

    cmd = "ovs-ofctl dump-flows br0 -O Openflow13 | grep 'table=%s' | grep %s | wc -l" % (l3output, ip)

    result = check_flow_table(host_map[host], cmd)

    assert int(result) <= 0


@then('check l3 logicalport ping "{host1}" "{name1}" "{ip1}" "{host2}" "{name2}" "{ip2}" success')
def check_l3_ping_sucess(context, host1, name1, ip1, host2, name2, ip2):
    host_map = {"host1": context.host1, "host2": context.host2}

    flag = name1[-1:]
    ns = "ns" + flag

    # test ping
    cmd = "ip netns exec %s ping %s -w 10 -c 5" % (ns,ip2)
    result = call_in_docker(host_map[host1],cmd)

    pattern = re.compile("(\d)% packet loss")

    match = pattern.search(result)
    assert match is not None

    if match:
        loss = int(match.groups()[0])
        assert loss <= 10


@then('check l3 logicalport ping "{host1}" "{name1}" "{ip1}" "{host2}" "{name2}" "{ip2}" fail')
def check_l3_ping_fail(context, host1, name1, ip1, host2, name2, ip2):

    host_map = {"host1": context.host1, "host2": context.host2}

    flag = name1[-1:]
    ns = "ns" + flag

    # test ping
    try:
        cmd = "ip netns exec %s ping %s -w 10 -c 5" % (ns,ip2)
        result = call_in_docker(host_map[host1],cmd)
    except Exception:
        pass
    else:
        raise AssertionError


@given('update logicalport name "{id}" "{name}"')
def update_logicalport_name(context, id, name):

    c = update_logical_port(id=id, name = name)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@given('update logicalnetwork name "{id}" "{name}"')
def update_logicalnet_name(context, id, name):

    c = update_logical_network(id=id, name = name)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@given('update physicalnetwork name "{id}" "{name}"')
def update_physicalnetwork_name(context, id, name):

    c = update_physicalnetwork_network(id=id, name = name)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@given('update physicalport "{name}" test "{attr}"')
def update_physical_port_attr(context, name, attr):

    c = update_physical_port(name=name , test=attr)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@given('update subnet name "{id}" "{name}"')
def update_subnet_name(context, id, name):

    c = update_subnet(id=id, name = name)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@given('update subnet gateway "{id}" "{gateway}"')
def update_subnet_gateway(context, id, gateway):

    c = update_subnet(id=id, gateway = gateway)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@given('update router name "{id}" "{name}"')
def update_router_name(context, id, name):

    c = update_router_network(id=id, name = name)

    command = "curl -s '%s'" % c

    call_in_docker(context.host1, command)


@then('check logicalport name "{id}" "{name}"')
def check_logical_port_name(context, id, name):

    c = list_logical_port()
    command = "curl -s '%s'" % c
    result = call_in_docker(context.host1, command)
    msg = json.loads(result)

    assert len(msg['result']) >= 1

    c = list_logical_port(id=id)

    command = "curl -s '%s'" % c

    result = call_in_docker(context.host1, command)

    msg = json.loads(result)

    assert 'name' in msg['result'][0] and msg['result'][0]['name'] == name

@then('check logicalnetwork name "{id}" "{name}"')
def check_logical_network_name(context, id, name):

    c = list_logical_network()
    command = "curl -s '%s'" % c
    result = call_in_docker(context.host1, command)
    msg = json.loads(result)

    assert len(msg['result']) >= 1

    c = list_logical_network(id=id)

    command = "curl -s '%s'" % c

    result = call_in_docker(context.host1, command)

    msg = json.loads(result)

    assert 'name' in msg['result'][0] and msg['result'][0]['name'] == name


@then('check physicalnetwork name "{id}" "{name}"')
def check_physical_network_name(context, id, name):

    c = list_physical_network()
    command = "curl -s '%s'" % c
    result = call_in_docker(context.host1, command)
    msg = json.loads(result)

    assert len(msg['result']) >= 1

    c = list_physical_network(id=id)

    command = "curl -s '%s'" % c

    result = call_in_docker(context.host1, command)

    msg = json.loads(result)

    assert 'name' in msg['result'][0] and msg['result'][0]['name'] == name

@then('check physicalport "{name}" test "{attr}"')
def check_physical_port_attr(context, name, attr):

    c = list_physical_port()
    command = "curl -s '%s'" % c
    result = call_in_docker(context.host1, command)
    msg = json.loads(result)

    assert len(msg['result']) >= 1

    c = list_physical_port(name=name)

    command = "curl -s '%s'" % c

    result = call_in_docker(context.host1, command)

    msg = json.loads(result)

    assert 'test' in msg['result'][0] and msg['result'][0]['test'] == attr


@then('check subnet name "{id}" "{name}"')
def check_subnet_name(context, id, name):

    c = list_subnet()
    command = "curl -s '%s'" % c
    result = call_in_docker(context.host1, command)
    msg = json.loads(result)

    assert len(msg['result']) >= 1

    c = list_subnet(id=id)

    command = "curl -s '%s'" % c

    result = call_in_docker(context.host1, command)

    msg = json.loads(result)

    assert 'name' in msg['result'][0] and msg['result'][0]['name'] == name


@then('check router name "{id}" "{name}"')
def check_router_name(context, id, name):

    c = list_router()
    command = "curl -s '%s'" % c
    result = call_in_docker(context.host1, command)
    msg = json.loads(result)

    assert len(msg['result']) >= 1

    c = list_router(id=id)

    command = "curl -s '%s'" % c

    result = call_in_docker(context.host1, command)

    msg = json.loads(result)

    assert 'name' in msg['result'][0] and msg['result'][0]['name'] == name


@then('remove subnet "{id}"')
def remove_special_subnet(context, id):

    c = remove_subnet(id=id)
    command = "curl -s '%s'" % c

    result = call_in_docker(context.host1, command)

    msg = json.loads(result)

    assert 'status' in msg['result'] and msg['result']['status'] == 'OK'



@then('remove logicalnetwork "{id}"')
def remove_special_logicalnetwork(context, id):

    c = remove_logical_network(id=id)
    command = "curl -s '%s'" % c

    result = call_in_docker(context.host1, command)

    msg = json.loads(result)

    assert 'status' in msg['result'] and msg['result']['status'] == 'OK'


@then('remove physicalnetwork "{id}"')
def remove_special_physicalnetwork(context, id):

    c = remove_physical_network(id=id)
    command = "curl -s '%s'" % c

    result = call_in_docker(context.host1, command)

    msg = json.loads(result)

    assert 'status' in msg['result'] and msg['result']['status'] == 'OK'