import urllib
import time

from utils import call_in_docker

endpoint = 'http://127.0.0.1:8081'

try:
    from urllib import urlencode
except Exception:
    from urllib.parse import urlencode


def create_physical_network(id, type = "vlan",**kwargs):

    params = {"id":id, "type": type}

    if type == "vlan":
        params.update({"vlanrange":"`[[100,1000]]`"})
    elif type == "vxlan":
        params.update({"vnirange":"`[[1000,2000]]`"})

    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/createphysicalnetwork?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return url

def update_physicalnetwork_network(id, **kwargs):

    params = {"id":id}
    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/updatephysicalnetwork?%s" % params

    return url


def list_physical_network(**kwargs):

    params = {}
    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/listphysicalnetworks?%s" % params

    return url


def remove_physical_network(id):

    params = {'id':id}

    params = urlencode(params)

    url = endpoint + "/viperflow/deletephysicalnetwork?%s" % params

    return url


def create_logical_network(id, physicalnetwork, **kwargs):

    params = {"id":id, "physicalnetwork":physicalnetwork}

    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/createlogicalnetwork?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return url

def update_logical_network(id, **kwargs):

    params = {"id":id}
    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/updatelogicalnetwork?%s" % params

    return url


def list_logical_network(**kwargs):

    params = {}
    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/listlogicalnetworks?%s" % params

    return url

def remove_logical_network(id):

    params = {"id":id}

    params = urlencode(params)

    url = endpoint + "/viperflow/deletelogicalnetwork?%s" % params

    return url

def create_logical_port(id, logicalnetwork, **kwargs):

    params = {"id":id, "logicalnetwork": logicalnetwork}

    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/createlogicalport?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return url


def remove_logical_port(id):

    params = {"id":id}

    params = urlencode(params)

    url = endpoint + "/viperflow/deletelogicalport?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return url

def update_logical_port(id, **kwargs):

    params = {"id":id}
    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/updatelogicalport?%s" % params

    return url

def list_logical_port(**kwargs):

    params = {}
    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/listlogicalports?%s" % params

    return url


def create_physical_port(name, physicalnetwork, **kwargs):

    params = {"name":name, "physicalnetwork": physicalnetwork}

    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/createphysicalport?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return url

def update_physical_port(name,**kwargs):

    params = {"name":name}
    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/updatephysicalport?%s" % params

    return url


def list_physical_port(**kwargs):

    params = {}
    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/listphysicalports?%s" % params

    return url


def remove_physical_port(name):


    params = {"name":name}

    params = urlencode(params)

    url = endpoint + "/viperflow/deletephysicalport?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return url


def create_subnet(subnet_id, logicalnetwork, cidr, gateway, **kwargs):

    params = {"id":subnet_id, "logicalnetwork": logicalnetwork,
              "cidr": cidr, "gateway": gateway}

    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/createsubnet?%s" % params

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return url

def update_subnet(id, **kwargs):

    params = {"id":id}
    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/updatesubnet?%s" % params

    return url


def list_subnet(**kwargs):
    params = {}
    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/listsubnets?%s" % params

    return url

def remove_subnet(id):

    params = {"id":id}

    params = urlencode(params)

    url = endpoint + "/viperflow/deletesubnet?%s" % params

    return url


def create_router(id,**kwargs):

    pararms = {"id":id}

    pararms.update(kwargs)

    pararms = urlencode(pararms)

    url = endpoint + "/vrouterapi/createvirtualrouter?%s" % pararms

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return url

def update_router_network(id, **kwargs):

    params = {"id":id}
    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/vrouterapi/updatevirtualrouter?%s" % params

    return url


def list_router(**kwargs):

    params = {}
    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/vrouterapi/listvirtualrouters?%s" % params

    return url

def remove_virtual_router(id):

    params = {"id":id}

    params = urlencode(params)

    url = endpoint + "/vrouterapi/deletevirtualrouter?%s" % params

    return url


def add_router_interface(router,subnet, **kwargs):

    params = {"router":router, "subnet": subnet}

    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/vrouterapi/addrouterinterface?%s" % params

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return url


def del_router_interface(router, subnet, **kwargs):

    params = {"router":router, "subnet": subnet}

    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/vrouterapi/removerouterinterface?%s" % params

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return url


def list_router_interface(id):

    params = {"id":id}
    params = urlencode(params)

    url = endpoint + "/vrouterapi/listrouterinterfaces?%s" % params

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return url

def list_vtep_bridge(**kwargs):

    params = {}
    params.update(kwargs)

    params = urlencode(params)
    url = endpoint + "/vtepcontroller/listphysicalswitches?%s" % params

    return url


def list_vtep_controller_bridge_interface(**kwargs):
    params = {}
    params.update(kwargs)

    params = urlencode(params)
    url = endpoint + "/vtepcontroller/listphysicalports?%s" % params

    return url


def check_flow_table(host, cmd):

    time.sleep(2)

    result = call_in_docker(host,cmd)

    return result
