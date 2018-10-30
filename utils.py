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

    db = "redis"
    if 'db' in context.config.userdata:
        db = context.config.userdata['db']
        if db == 'zookeeper':
            db = "jplock/zookeeper"

    kvdb_docker = create_docker(db)

    # store docker instance id to context
    context.kvdb = kvdb_docker

    # 2. we should rewrite kvdb url to every conf file
    kvdb_ip_address = get_docker_ip(kvdb_docker)

    config_path = os.getcwd() + "/config"
    kvdb_url_format = re.compile(r'(module.redisdb.url=*)')
    kvdb_url_format2 = re.compile(r'(module.zookeeperdb.url=*)')
    kvdb_url_format3 = re.compile(r'(proxy.kvstorage=*)')
    kvdb_url_format4 = re.compile(r'(proxy.updatenotifier=)')
    for file in os.listdir(config_path):
        if file.endswith(".conf"):
            # config file is so small, so read all .. write all
            with open(config_path + "/" + file) as f:
                lines = [line for line in f.readlines() if not kvdb_url_format.match(line)
                         and not kvdb_url_format2.match(line)
                         and not kvdb_url_format3.match(line)
                         and not kvdb_url_format4.match(line)]
                if 'db' in context.config.userdata and context.config.userdata['db'] == "zookeeper":
                    url = "module.zookeeperdb.url='tcp://%s:2181'" % str(kvdb_ip_address)
                    lines.append(url)
                    lines.append('\n')

                    proxy = "proxy.kvstorage='vlcp.service.connection.zookeeperdb.ZooKeeperDB'"
                    lines.append(proxy)
                    lines.append('\n')

                    proxy_notify = "proxy.updatenotifier='vlcp.service.connection.zookeeperdb.ZooKeeperDB'"
                    lines.append(proxy_notify)

                else:
                    url = "module.redisdb.url='tcp://%s'" % str(kvdb_ip_address)
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

    logger.info(" init vtep controller")
    vtep1 = create_docker(base_image)
    context.vtep1 = vtep1
    init_docker_host(context, vtep1)

    vtep2 = create_docker(base_image)
    context.vtep2 = vtep2
    init_docker_host(context, vtep2)

def uninit_environment(context):

    if hasattr(context, "bridge"):
        if hasattr(context, "host1"):
            remove_host_vlan_interface(context.bridge, context.host1)

        if hasattr(context, "host2"):
            remove_host_vlan_interface(context.bridge, context.host2)
        if getattr(context, 'failed', False):
            print_log_in_docker(context.bridge)
        remove_docker(context.bridge)
        # in differnet level , we can not del attr
        # delattr(context, "bridge")

    if hasattr(context, "kvdb"):
        remove_docker(context.kvdb)
        # delattr(context, "kvdb")

    if hasattr(context, "host1"):
        remove_host_vxlan_interface(context.host1)
        if getattr(context, 'failed', False):
            print_log_in_docker(context.host1)
        remove_docker(context.host1)
        # delattr(context, "host1")

    if hasattr(context, "host2"):
        remove_host_vxlan_interface(context.host2)
        if getattr(context, 'failed', False):
            print_log_in_docker(context.host2)
        remove_docker(context.host2)
        # delattr(context, "host2")

    if hasattr(context, "vtep1"):
        if getattr(context, 'failed', False):
            print_log_in_docker(context.vtep1)
        remove_docker(context.vtep1)

    if hasattr(context, "vtep2"):
        if getattr(context, 'failed', False):
            print_log_in_docker(context.vtep2)
        remove_docker(context.vtep2)


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
    cmd = "/usr/share/openvswitch/scripts/ovs-ctl start --system-id=random"
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

            cmd = "ip link del veth%s" % i
            call_in_docker(host, cmd)

            cmd = "ip netns del ns%d" % i
            call_in_docker(host, cmd)
        except Exception:
            pass


def init_docker_bridge(bridge):

    # start ovs server
    cmd = "/usr/share/openvswitch/scripts/ovs-ctl start --system-id=random"
    call_in_docker(bridge, cmd)

    cmd = "ovs-vsctl add-br br0"
    call_in_docker(bridge, cmd)


def call_in_docker(docker, cmd):
    c = "docker exec %s %s" % (docker, cmd)
    return str_3_2(subprocess.check_output(c, shell=True))


def add_host_vxlan_interface(docker, local_ip, remote_ip):
    cmd = "ovs-vsctl add-port br0 vxlan0 -- set interface vxlan0 " \
          "type=vxlan options:key=flow options:local_ip=%s options:remote_ip=flow" % local_ip

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

    try_max = 10
    while os.path.isfile('/tmp/vlcp_test') and try_max > 0:
        time.sleep(2)
        try_max -= 1

    if try_max <= 0:
        raise ValueError("no chance to create bridge link errro")

    os.mknod('/tmp/vlcp_test')
    try:
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
    finally:
        os.remove('/tmp/vlcp_test')

    cmd = "ip netns exec %s ip link set %s up" % (bridge, "docker-"+docker[0:4])
    subprocess.check_call(cmd, shell=True)

    cmd = "ip netns exec %s ip link set %s up" % (docker, "bridge")
    subprocess.check_call(cmd, shell=True)

    cmd = "ovs-vsctl add-port br0 %s -- set interface %s external_ids:vtep-physname='br0' " \
          "external_ids:vtep-phyiname=%s" % ("bridge","bridge","docker-"+docker[0:4])
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


def copy_report_file_to_local(src_host):

    # copy file to tmp in src_host
    cmd = "bash -c 'cd /opt && mkdir tmp && cp report_file.* tmp'"
    call_in_docker(src_host, cmd)

    # copy file to local filesystem from docker
    cmd = "docker cp %s:/opt/tmp ." % src_host
    subprocess.check_call(cmd, shell=True)

def copy_report_file_to_host(dst_host, dst_file):
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
    
    cmd = "/opt/coverage xml --rcfile=/opt/coverage.conf -o /opt/coverage.xml -i"
    call_in_docker(host, cmd)

    cmd = "docker cp %s:/opt/coverage.xml ." % host
    subprocess.check_call(cmd, shell=True)
    
    cmd = "/opt/coverage html --rcfile=/opt/coverage.conf -i"
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


def init_vtep_bridge(bridge):

    # init vtep ovsdb
    cmd = "ovsdb-tool create /etc/openvswitch/vtep.db /usr/share/openvswitch/vtep.ovsschema"
    call_in_docker(bridge, cmd)

    cmd = "ovs-appctl -t ovsdb-server ovsdb-server/add-db /etc/openvswitch/vtep.db"
    call_in_docker(bridge, cmd)

    # add ovsdb remote
    cmd = "ovs-appctl -t ovsdb-server ovsdb-server/add-remote ptcp:6632"
    call_in_docker(bridge, cmd)

    # add physical switch
    cmd = "vtep-ctl add-ps br0"

    call_in_docker(bridge, cmd)

    # add tunnel_ip
    local_ip = get_docker_ip(bridge)
    cmd = "vtep-ctl set Physical_Switch br0 tunnel_ips=%s" % (local_ip)
    call_in_docker(bridge, cmd)

    # start vtep
    cmd = "bash -c 'PYTHONPATH=/usr/share/openvswitch/python python2 " \
          "/usr/share/openvswitch/scripts/ovs-vtep " \
          "--log-file=/var/log/openvswitch/ovs-vtep.log " \
          "--pidfile=/var/run/openvswitch/ovs-vtep.pid --detach br0'"
    call_in_docker(bridge, cmd)


def uninit_vtep_bridge(bridge):

    cmd = "vtep-ctl del-ps br0"

    call_in_docker(bridge, cmd)


def print_log_in_docker(docker):
    cmd = "bash -c 'cat /var/log/vlcp.error.log || true'"
    print(call_in_docker(docker, cmd))
