from behave import *
from apis import *
from utils import *

import time

@given('remove bridge "{host}"')
def remove_bridge(context, host):
    host_map = {"host1": context.host1, "host2": context.host2}

    cmd = "ovs-vsctl del-br br0"

    call_in_docker(host_map[host], cmd)

@then('add bridge "{host}"')
def add_bridge(context, host):
    host_map = {"host1": context.host1, "host2": context.host2}

    cmd = "ovs-vsctl add-br br0"

    call_in_docker(host_map[host], cmd)


@then('check get all bridge info "{host}"')
def check_bridge_info(context, host):
    
    host_map = {"host1": context.host1, "host2": context.host2}

    url = 'http://127.0.0.1:8081/ovsdbmanager/getallbridges'
    cmd = 'curl -s -m 2 "%s"' % url
    
    # restart vlcp , when some version python (eg: pypy-5.4) we need more time to call api
    time.sleep(2)
    
    # recv result means success
    try:
        call_in_docker(host_map[host], cmd)
    except Exception:
        raise ValueError(" check get bridge info error !")