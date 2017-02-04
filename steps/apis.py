import urllib
import urllib2

endpoint = 'http://127.0.0.1:8081'


def create_physical_network(id, type = "vlan",**kwargs):

    params = {"id":id, "type": type}

    if type == "vlan":
        params.update({"vlanrange":"`[[100,1000]]`"})
    elif type == "vxlan":
        params.update({"vnirange":"`[[1000,2000]]`"})

    params.update(kwargs)

    params = urllib.urlencode(params)

    url = endpoint + "/viperflow/createphysicalnetwork?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command


def create_logical_network(id, physicalnetwork, **kwargs):

    params = {"id":id, "physicalnetwork":physicalnetwork}

    params.update(kwargs)

    params = urllib.urlencode(params)

    url = endpoint + "/viperflow/createlogicalnetwork?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command


def create_logical_port(id, logicalnetwork, **kwargs):

    params = {"id":id, "logicalnetwork": logicalnetwork}

    params.update(kwargs)

    params = urllib.urlencode(params)

    url = endpoint + "/viperflow/createlogicalport?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command


def remove_logical_port(id):

    params = {"id":id}

    params = urllib.urlencode(params)

    url = endpoint + "/viperflow/deletelogicalport?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command


def create_physical_port(name, physicalnetwork, **kwargs):

    params = {"name":name, "physicalnetwork": physicalnetwork}

    params.update(kwargs)

    params = urllib.urlencode(params)

    url = endpoint + "/viperflow/createphysicalport?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command


def remove_physical_port(name):


    params = {"name":name}

    params = urllib.urlencode(params)

    url = endpoint + "/viperflow/deletephysicalport?%s" % params

    #f = urllib2.urlopen(url).read()

    command = "import urllib2; urllib2.urlopen('%s').read()" % url

    return command
