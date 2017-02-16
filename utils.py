import subprocess
import os
import re
import logging
import time
import json
import random

try:
    from shlex import quote as shell_quote
except Exception:
    from pipes import  quote as shell_quote

logger = logging.getLogger(__name__)


def init_environment(context, base_image):

    logger.info("init kvdb ..")
    # 1. create redis kvdb
    kvdb_docker = create_docker("redis")

    # store docker instance id to context
    context.kvdb = kvdb_docker

    # 2. we should rewrite kvdb url to every conf file
    kvdb_ip_address = get_docker_ip(kvdb_docker)

    config_path = os.getcwd() + "/config"
    kvdb_url_format = re.compile(r'(module.redisdb.url=*)')
    for file in os.listdir(config_path):
        if file.endswith(".conf"):
            # config file is so small, so read all .. write all
            with open(config_path + "/" + file) as f:
                lines = [line for line in f.readlines() if not kvdb_url_format.match(line)]
                url = "module.redisdb.url='http://%s'" % str(kvdb_ip_address)
                lines.append(url)

            with open(config_path + "/" + file, "w") as f:
                f.truncate()
                f.writelines(lines)

    logger.info("init host ..")
    # 3. start two docker container as host !
    host1 = create_docker(base_image)
    context.host1 = host1
    host1_ip_address = get_docker_ip(host1)

    host2 = create_docker(base_image)
    context.host2 = host2
    host2_ip_address = get_docker_ip(host2)

    init_docker_host(context, host1)
    init_docker_host(context, host2)

    logger.info("add vxlan interface ..")
    # add host vxlan interface
    add_host_vxlan_interface(host1, host1_ip_address, host2_ip_address)
    add_host_vxlan_interface(host2, host2_ip_address, host1_ip_address)

    # add host vlan interface

    logger.info("init bridge ..")
    # vlan interface , user other ovs bridge in docker
    bridge = create_docker(base_image)
    context.bridge = bridge
    init_docker_bridge(bridge)

    logger.info("add vlan interface ..")
    add_host_vlan_interface(bridge, host1)
    add_host_vlan_interface(bridge, host2)


def uninit_environment(context):

    if hasattr(context, "bridge"):
        if hasattr(context, "host1"):
            remove_host_vlan_interface(context.bridge, context.host1)

        if hasattr(context, "host2"):
            remove_host_vlan_interface(context.bridge, context.host2)

        remove_docker(context.bridge)
        # in differnet level , we can not del attr
        # delattr(context, "bridge")

    if hasattr(context, "kvdb"):
        remove_docker(context.kvdb)
        # delattr(context, "kvdb")

    if hasattr(context, "host1"):
        remove_host_vxlan_interface(context.host1)
        remove_docker(context.host1)
        # delattr(context, "host1")

    if hasattr(context, "host2"):
        remove_host_vxlan_interface(context.host2)
        remove_docker(context.host2)
        # delattr(context, "host2")


def create_docker(image):
    cmd = "docker run -it -d --privileged " + image

    kvdb_id = subprocess.check_output(cmd, shell=True)

    return str_3_2(kvdb_id.strip(b'\n'))


def remove_docker(image):
    cmd = "docker rm -f %s" % image
    subprocess.check_output(cmd, shell=True)


def get_docker_ip(docker):

    cmd = "docker inspect --format={{.NetworkSettings.Networks.bridge.IPAddress}} " + docker

    ip = subprocess.check_output(cmd, shell=True)

    return str_3_2(ip.strip(b'\n'))


def init_docker_host(context, docker):

    # install ovs ; do in base image Dockerfile

    # start ovs server
    cmd = "/usr/local/share/openvswitch/scripts/ovs-ctl start --system-id=random"
    call_in_docker(docker, cmd)

    # copy wheel file
    vlcp_wheel = "*.whl"

    if "vlcp" in context.config.userdata:
        vlcp_wheel = context.config.userdata["vlcp"]

    cmd = "docker cp %s %s:/opt" % (vlcp_wheel, docker)
    subprocess.check_call(cmd, shell=True)

    # install vlcp
    cmd = "/opt/pip install --upgrade /opt/%s" % vlcp_wheel
    c = "docker exec %s bash -c %s" % (docker, shell_quote(cmd))
    subprocess.check_output(c, shell=True)

    if "coverage" in context.config.userdata:
        cmd = "docker cp %s %s:/opt" % ("coverage.conf", docker)
        subprocess.check_call(cmd, shell=True)

        cmd = "sed -i 's~/opt/python~/opt/coverage run --rcfile=/opt/coverage.conf~g' %s" % "supervisord.conf"
        subprocess.check_call(cmd, shell=True)
    else:
        cmd = "sed -i 's~/opt/coverage run --rcfile=/opt/coverage.conf~/opt/python~g' %s" % "supervisord.conf"
        subprocess.check_call(cmd, shell=True)

    # copy supervisor conf to host
    cmd = "docker cp %s %s:/etc" % ("supervisord.conf",docker)
    subprocess.check_call(cmd, shell=True)

    # start supervisord
    cmd = "supervisord -c /etc/supervisord.conf"
    call_in_docker(docker, cmd)

    # add ovs bridge br0
    cmd = "ovs-vsctl add-br br0"
    call_in_docker(docker, cmd)

    # set br0 controller to 127.0.0.1
    cmd = "ovs-vsctl set-controller br0 tcp:127.0.0.1"
    call_in_docker(docker, cmd)


def copy_file_to_host(src_file, host, dst_file):

    cmd = "docker cp %s %s:%s" % (src_file, host, dst_file)
    subprocess.check_call(cmd, shell=True)


def clear_host_ns_env(context,host):

    # we will add namespace as host in docker ,
    # clear all namespace

    for i in range(1,10):
        try:
            cmd = "ovs-vsctl del-port veth%d 2>/dev/null 1>/dev/null" % i
            call_in_docker(host, cmd)

            cmd = "ip netns del ns%d" % i
            call_in_docker(host, cmd)
        except Exception:
            pass


def init_docker_bridge(bridge):

    # start ovs server
    cmd = "/usr/local/share/openvswitch/scripts/ovs-ctl start --system-id=random"
    call_in_docker(bridge, cmd)

    cmd = "ovs-vsctl add-br br0"
    call_in_docker(bridge, cmd)


def call_in_docker(docker, cmd):
    c = "docker exec %s %s" % (docker, cmd)
    return str_3_2(subprocess.check_output(c, shell=True))


def add_host_vxlan_interface(docker, local_ip, remote_ip):
    cmd = "ovs-vsctl add-port br0 vxlan0 -- set interface vxlan0 " \
          "type=vxlan options:key=flow options:local_ip=%s options:remote_ip=%s" % (local_ip, remote_ip)

    call_in_docker(docker, cmd)


def remove_host_vxlan_interface(docker):
    pass


def add_host_vlan_interface(bridge, docker):

    # create link file , so we can operate network namespace
    link_docker_namespace(bridge)
    link_docker_namespace(docker)

    # init vlan host , we create link named bridge , to set it to ns
    # when more instance , it mybe conflict error
    time.sleep(random.randint(0,10))

    # some case , link bridge will not destory auto to case next crate failed
    # try delete it first
    cmd = "ip link del bridge 2>/dev/null 1>/dev/null"
    try:
        subprocess.check_call(cmd,shell=True)
    except Exception:
        pass


    # create veth pair link bridge and docker
    cmd = "ip link add %s type veth peer name %s" % ("docker-"+docker[0:4], "bridge")
    subprocess.check_call(cmd, shell=True)

    # add link to namespace
    cmd = "ip link set %s netns %s" % ("bridge", docker)
    subprocess.check_call(cmd, shell=True)
    cmd = "ip link set %s netns %s" % ("docker-"+docker[0:4], bridge)
    subprocess.check_call(cmd, shell=True)

    cmd = "ip netns exec %s ip link set %s up" % (bridge, "docker-"+docker[0:4])
    subprocess.check_call(cmd, shell=True)

    cmd = "ip netns exec %s ip link set %s up" % (docker, "bridge")
    subprocess.check_call(cmd, shell=True)

    cmd = "ovs-vsctl add-port br0 %s" % "bridge"
    call_in_docker(docker, cmd)

    cmd = "ovs-vsctl add-port br0 %s" % "docker-"+docker[0:4]
    call_in_docker(bridge, cmd)

    unlink_docker_namespace(bridge)
    unlink_docker_namespace(docker)


def remove_host_vlan_interface(bridge, docker):

    cmd = "ip link del %s" % "bridge"
    call_in_docker(docker, cmd)


def link_docker_namespace(docker):

    # get docker pid
    cmd = "docker inspect --format={{.State.Pid}} %s" % docker
    pid = subprocess.check_output(cmd, shell=True)
    pid = str_3_2(pid.strip(b'\n'))

    # link docker namespace file
    cmd = "ln -sf /proc/%s/ns/net /var/run/netns/%s" % (pid, docker)
    subprocess.check_call(cmd, shell=True)


def unlink_docker_namespace(docker):
    cmd = "rm /var/run/netns/%s" % docker
    subprocess.check_call(cmd, shell=True)


def clear_kvdb(context, cmd):
    if hasattr(context, "kvdb"):
        kvdb = context.kvdb

        call_in_docker(kvdb, cmd)


def restart_vlcp_controller(host):

    cmd = "supervisorctl restart vlcp"
    call_in_docker(host, cmd)

    time.sleep(5)


def copy_file_host_2_host(src_host, dst_host, src_file, dst_file):

    #cmd = "mkdir %s" % tmp
    #subprocess.check_call(cmd, shell=True)

    # copy file to tmp in src_host
    cmd = "bash -c 'cd /opt && mkdir tmp && cp report_file.* tmp'"
    call_in_docker(src_host, cmd)

    # copy file to local filesystem from docker
    cmd = "docker cp %s:/opt/tmp ." % src_host
    subprocess.check_call(cmd, shell=True)

    # copy file to host from filesystem
    cmd = "docker cp tmp %s:%s" % (dst_host, dst_file)
    subprocess.check_call(cmd, shell=True)



def collect_coverage_report(host, file):

    cmd = "mkdir /opt/coverage_report"
    call_in_docker(host, cmd)

    # copy /opt/tmp/report_file to /opt that from other host
    cmd = "bash -c 'cd /opt && cp tmp/* .'"
    call_in_docker(host, cmd)


    cmd = "bash -c 'cd /opt && cp report_file.* coverage_report'"
    call_in_docker(host, cmd)

    cmd = "/opt/coverage combine --rcfile=/opt/coverage.conf"
    call_in_docker(host, cmd)

    cmd = "/opt/coverage html --rcfile=/opt/coverage.conf"
    call_in_docker(host, cmd)

    cmd = "docker cp %s:/opt/html_file ." % host
    subprocess.check_call(cmd, shell=True)

    cmd = "docker cp %s:/opt/coverage_report ." % host
    subprocess.check_call(cmd, shell=True)


def get_flow_map(host):

    url = "http://127.0.0.1:8081/openflowmanager/lastacquiredtables"

    cmd = 'curl -s "%s"' % url

    result = call_in_docker(host, cmd)

    msg = json.loads(result)

    map = dict(msg['result'][0])

    return map


def str_3_2(data):
    # when python3 ip is b'' not ''
    if isinstance(data, type(b'')) and not isinstance(data, type('')):
        # run in python3
        data = data.decode('utf-8')

    return data
