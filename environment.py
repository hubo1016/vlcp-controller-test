import logging
import sys

from utils import *

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
    
    uninit_environment(context)


def before_feature(context, feature):

    try:
        # every feature , clear kvdb , clear environment
        cmd = "redis-cli FLUSHALL"
        clear_kvdb(context, cmd)

        if hasattr(context, "host1"):
            clear_host_ns_env(context, context.host1)
            prepare_config_file(context, feature)
            restart_vlcp_controller(context.host1)

        if hasattr(context, "host2"):
            clear_host_ns_env(context, context.host2)
            prepare_config_file(context, feature)
            restart_vlcp_controller(context.host2)
    except Exception:
        logger.warning("init feature %s error", feature.name , exc_info=True)
        uninit_environment(context)
        sys.exit(-1)

def after_feature(context, feature):
    pass


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
        "l2switch controller learning" : "l2switch2.conf"
    }

    config_file = "config/%s" % "ioprocess.conf"

    if feature.name in config_file_map:
        config_file = "config/%s" % config_file_map[feature.name]

        copy_file_to_host(config_file, context.host1, "/etc/vlcp.conf")
        copy_file_to_host(config_file, context.host2, "/etc/vlcp.conf")



