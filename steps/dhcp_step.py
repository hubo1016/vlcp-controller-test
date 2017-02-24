from behave import *
from utils import *


@given('dhcp get ip "{host}" "{vethname}"')
@when('dhcp get ip "{host}" "{vethname}"')
def dhcp(context, host, vethname):
    host_map = {"host1": context.host1, "host2": context.host2}

    flag = vethname[-1:]
    ns = "ns" + flag
    veth = "vethns" + flag

    cmd = "ip netns exec %s dhclient %s" % (ns, veth)

    call_in_docker(host_map[host], cmd)


@given('check get ip "{host}" "{vethname}" "{ip}"')
@then('check get ip "{host}" "{vethname}" "{ip}"')
def check_ip(context, host, vethname, ip):

    host_map = {"host1": context.host1, "host2": context.host2}

    flag = vethname[-1:]
    ns = "ns" + flag
    veth = "vethns" + flag

    cmd = "ip netns exec %s ip addr show %s | awk '/inet/{print substr($2,0,length($2)-3)}'" % (ns, veth)

    get_ip = call_in_docker(host_map[host], cmd)

    assert get_ip[0:len(ip)] == ip

