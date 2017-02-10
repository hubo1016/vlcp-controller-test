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

    return command


def create_logical_network(id, physicalnetwork, **kwargs):

    params = {"id":id, "physicalnetwork":physicalnetwork}

    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/createlogicalnetwork?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command


def create_logical_port(id, logicalnetwork, **kwargs):

    params = {"id":id, "logicalnetwork": logicalnetwork}

    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/createlogicalport?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command


def remove_logical_port(id):

    params = {"id":id}

    params = urlencode(params)

    url = endpoint + "/viperflow/deletelogicalport?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command


def create_physical_port(name, physicalnetwork, **kwargs):

    params = {"name":name, "physicalnetwork": physicalnetwork}

    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/createphysicalport?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command


def remove_physical_port(name):


    params = {"name":name}

    params = urlencode(params)

    url = endpoint + "/viperflow/deletephysicalport?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command


def create_subnet(subnet_id, logicalnetwork, cidr, gateway, **kwargs):

    params = {"id":subnet_id, "logicalnetwork": logicalnetwork,
              "cidr": cidr, "gateway": gateway}

    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/viperflow/createsubnet?%s" % params

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command


def create_router(id,**kwargs):

    pararms = {"id":id}

    pararms.update(kwargs)

    pararms = urlencode(pararms)

    url = endpoint + "/vrouterapi/createvirtualrouter?%s" % pararms

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command


def add_router_interface(router,subnet, **kwargs):

    params = {"router":router, "subnet": subnet}

    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/vrouterapi/addrouterinterface?%s" % params

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command

def del_router_interface(router, subnet, **kwargs):


    params = {"router":router, "subnet": subnet}

    params.update(kwargs)

    params = urlencode(params)

    url = endpoint + "/vrouterapi/removerouterinterface?%s" % params

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command



def check_flow_table(host, cmd):

    time.sleep(2)

    result = call_in_docker(host,cmd)

    return result
