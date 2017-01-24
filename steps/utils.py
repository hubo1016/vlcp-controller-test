import subprocess

def init_environment(context,env):
    pass


def call_in_docker(host, cmd):
    c = "docker exec %s %s" % (host, cmd)

    subprocess.check_output(c, shell=True)

