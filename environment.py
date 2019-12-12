import logging
import sys

from utils import *
from jinja2 import Environment, FileSystemLoader

logging.basicConfig()
logger = logging.getLogger(__name__)


def before_all(context):
    base = "vlcp-controller/test"
    tag = "python2.7"
    
    if "tag" in context.config.userdata:
        tag = context.config.userdata["tag"]

    if "base" in context.config.userdata:
        base = context.config.userdata["base"]

    docker_base_image = base + ":" + tag

    try:
        init_environment(context, docker_base_image)
    except Exception:
        logger.warning("init environment error ", exc_info=True)
        uninit_environment(context)
        sys.exit(-1)


def after_all(context):
    if "coverage" in context.config.userdata:
        # to collect all coverage report file , restart vlcp controller
        restart_vlcp_controller(context.host1)
        restart_vlcp_controller(context.host2)
        restart_vlcp_controller(context.vtep1)
        restart_vlcp_controller(context.vtep2)
        # collect coverage report

        # copy report file from host2 to host1
        #copy_file_host_2_host(context.host2, context.host1, "/opt/report.*", "/opt")
        copy_report_file_to_local(context.host2)
        copy_report_file_to_local(context.vtep1)
        copy_report_file_to_local(context.vtep2)

        copy_report_file_to_host(context.host1, "/opt")

        collect_coverage_report(context.host1, "coverage_report.tar.gz")

    uninit_environment(context)


def before_feature(context, feature):

    try:
        # every feature , clear kvdb , clear environment
        cmd = "redis-cli FLUSHALL"
        if 'db' in context.config.userdata:
            if context.config.userdata['db'] == "zookeeper":
                cmd = "bin/zkCli.sh rmr /vlcp || echo not exists"
        clear_kvdb(context, cmd)

        if hasattr(context, "host1"):
            clear_host_ns_env(context, context.host1)
            prepare_config_file(context, feature)
            restart_vlcp_controller(context.host1)

            # restart controller , to get flow name number map used in check

            flow_map = get_flow_map(context.host1)
            context.host1_flow_map = flow_map

        if hasattr(context, "host2"):
            clear_host_ns_env(context, context.host2)
            prepare_config_file(context, feature)
            restart_vlcp_controller(context.host2)

            flow_map = get_flow_map(context.host2)
            context.host2_flow_map = flow_map

        if feature.name in ["ioprocessing vxlan vtep"]:
            # prepare vtep env
            # 1. copy vtep config to host1
            prepare_vtep_template_config_file(context, feature, context.host1)
            restart_vlcp_controller(context.host1)

            # 2. reinit bridge
            init_vtep_bridge(context.bridge)

            # 3. copy vtep controller config to vtep
            prepare_vtep_controller_config_file(context, feature)
            restart_vlcp_controller(context.vtep1)
            restart_vlcp_controller(context.vtep2)


    except Exception:
        logger.warning("init feature %s error", feature.name , exc_info=True)
        uninit_environment(context)
        sys.exit(-1)


def after_feature(context, feature):

    if feature.name in ["ioprocessing vxlan vtep"]:
        uninit_vtep_bridge(context.bridge)
        
        # discard all flows manaul , restart ovs can't delete flows bind with vtep
        cmd = "ovs-ofctl del-flows br0"
        call_in_docker(context.bridge, cmd)
        
        # install normal flow
        cmd = "ovs-ofctl add-flow br0 action=normal"
        call_in_docker(context.bridge, cmd)


def prepare_config_file(context, feature):
    # every feature mybe have different config
    # so here map  feature name : config file
    config_file_map = {
        "ioprocessing vlan": "ioprocess.conf",
        "ioprocessing vxlan prepush": "ioprocess.conf",
        "ioprocessing vxlan flow learning": "ioprocess1.conf",
        "ioprocessing vxlan controller learning": "ioprocess2.conf",
        "l2switch prepush":"l2switch.conf",
        "l2switch flow learning" : "l2switch1.conf",
        "l2switch controller learning" : "l2switch2.conf",
        "l3switch arp prepush" : "l3switch.conf",
        "l3switch arp learn" : "l3switch1.conf",
        "l3switch external network" : "l3switch2.conf",
        "dhcp client" : "dhcp.conf",
        "failover" : "failover.conf",
        "ioprocessing vxlan vtep" : "ioprocess.conf"
    }

    config_file = "config/%s" % "ioprocess.conf"

    if feature.name in config_file_map:
        config_file = "config/%s" % config_file_map[feature.name]

        copy_file_to_host(config_file, context.host1, "/etc/vlcp.conf")
        copy_file_to_host(config_file, context.host2, "/etc/vlcp.conf")


def prepare_vtep_controller_config_file(context, feature):

    # produce config from template
    loader = FileSystemLoader("./config")
    env = Environment(loader=loader)
    template = env.get_template('vtepcontroller.tpl')

    config_name = 'tmp.conf'
    bridge_ip = get_docker_ip(context.bridge)
    kvdb_ip = get_docker_ip(context.kvdb)

    if 'db' in context.config.userdata and context.config.userdata['db'] == "zookeeper":
        zookeeper_db = "module.zookeeperdb.url='tcp://%s/'" % kvdb_ip
        db_proxy = "proxy.kvstorage='vlcp.service.connection.zookeeperdb.ZooKeeperDB'"
        proxy_notifier = "proxy.updatenotifier='vlcp.service.connection.zookeeperdb.ZooKeeperDB'"
        template.stream(bridge=bridge_ip, zookeeper_db=zookeeper_db,
                        db_proxy=db_proxy, proxy_notifier = proxy_notifier).dump(config_name)
    else:
        redis_db = "module.redisdb.url='tcp://%s/'" % kvdb_ip
        template.stream(bridge=bridge_ip, redis_db=redis_db).dump(config_name)

    copy_file_to_host(config_name, context.vtep1, "/etc/vlcp.conf")
    copy_file_to_host(config_name, context.vtep2, "/etc/vlcp.conf")


def prepare_vtep_template_config_file(context, feature, host):

    # produce config from template
    loader = FileSystemLoader("./config")
    env = Environment(loader=loader)
    template = env.get_template('vtep.tpl')

    config_name = 'tmp.conf'

    vtepcontroller1 = get_docker_ip(context.vtep1)
    vtepcontroller2 = get_docker_ip(context.vtep2)
    kvdb_ip = get_docker_ip(context.kvdb)

    if 'db' in context.config.userdata and context.config.userdata['db'] == "zookeeper":
        zookeeper_db = "module.zookeeperdb.url='tcp://%s/'" % kvdb_ip
        db_proxy = "proxy.kvstorage='vlcp.service.connection.zookeeperdb.ZooKeeperDB'"
        proxy_notifier = "proxy.updatenotifier='vlcp.service.connection.zookeeperdb.ZooKeeperDB'"
        template.stream(vtepcontroller1=vtepcontroller1,vtepcontroller2=vtepcontroller2, zookeeper_db=zookeeper_db,
                        db_proxy=db_proxy, proxy_notifier = proxy_notifier).dump(config_name)
    else:
        redis_db = "module.redisdb.url='tcp://%s/'" % kvdb_ip
        template.stream(vtepcontroller1=vtepcontroller1,
                        vtepcontroller2=vtepcontroller2,
                        redis_db=redis_db).dump(config_name)

    copy_file_to_host(config_name, host, "/etc/vlcp.conf")