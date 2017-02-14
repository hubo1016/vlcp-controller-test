import subprocess

from jinja2 import Environment, FileSystemLoader

parser = argparse.ArgumentParser()

parser.add_argument("base", help="special docker images base")
parser.add_argument('-ovs_version', help='special ovs version', default='2.5.1')
parser.add_argument("-name", help="special docker images name", default='vlcp_controller/test')
parser.add_argument("-tag", help="special docker images tag", default='python2.7')

args = parser.parse_args()

print('base_python_version', args.base_python_version)
print('ovs_version', args.ovs_version)
print('imags name', args.name)
print('image tag', args.tag)

loader = FileSystemLoader('.')

env = Environment(loader=loader)

template = env.get_template('Dockerfile')

dockerfile_name = 'Dockerfile_' + args.tag
template.stream(base=args.base_python_version, ovs_version=args.ovs_version).dump(dockerfile_name)

build_cmd = "docker build . -t %s:%s -f %s" % (args.name, args.tag, dockerfile_name)

print(build_cmd)

subprocess.check_call(build_cmd, shell=True)


