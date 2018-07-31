#server.debugging=True
module.jsonrpcserver.vhost.vtep.ovsdb=True
module.jsonrpcserver.vhost.vtep.client=True
module.jsonrpcserver.vhost.vtep.url='tcp://{{bridge}}:6632'


module.httpserver.url=None
module.httpserver.vhost.api.url='tcp://0.0.0.0:8081'
#module.httpserver.vhost.docker.url='unix:///run/docker/plugins/vlcp.sock'
#module.console.startinconsole=True
server.logging.version=1
server.logging.formatters={'fileFormatter':{'format':'%(asctime)s %(levelname)s %(name)s: %(message)s'}}
server.logging.handlers={'fileHandler':{'class':'logging.handlers.TimedRotatingFileHandler',
                                        'formatter':'fileFormatter',
                                        'filename':'/var/log/vlcp.log',
                                        'when':'midnight',
                                        'interval':1,
                                        'backupCount':7},
                         'fileHandler2':{'class':'logging.handlers.FileHandler',
                                        'formatter':'fileFormatter',
                                        'filename':'/var/log/vlcp.error.log',
                                        'level':'WARNING'}}
server.logging.root={'level':'INFO',
                     'handlers':['fileHandler','fileHandler2']}
#protocol.openflow.debugging = True
#protocol.redis.debugging = True
#module.l2switch.learning=False
#module.l2switch.nxlearn=False

#module.vxlancast.learning=False
#module.vxlancast.prepush=False

server.startup = (
                  'vlcp.service.manage.modulemanager.Manager',
                  'vlcp.service.manage.webapi.WebAPI',
                  'vlcp.service.sdn.vtepcontroller.VtepController'
                  )

{{redis_db}}
{{zookeeper_db}}
{{db_proxy}}
{{proxy_notifier}}
