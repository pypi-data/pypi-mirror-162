from .consul_handle import consul_reader
from .log import logger
import requests
import sys


class Kong:
    def __init__(self):

        self.admin_uri = consul_reader.service_as_url('kong',tag='admin')
        srv = consul_reader.read_service('kong',tag='kong')
        self.ip = srv.ip
        self.port = srv.port

    def register_upstream_service(self,upstream_name,port, base_path,auth=None,**args):
        self.register_upstream(upstream_name,consul_reader.agent.combine_address(port),**args)
        self.register_service(upstream_name,base_path,auth)

    def register_service(self,upstream_name,base_path, auth=None):
        '''
        :param kong_admin: 用于注册服务
        :param service_host: 本地服务的host，用于设定upstream_url
        :param service: 服务api，如：rightmanage/v1.0
        :param kong_uris: 空的host uris，为空时值为service,如：rightmanage/v1.0
        :param auth: 认证类型，可为str或list，如：'jwt'，或：['jwt','key']
        :param health: 如果service_host 是upstreams，则可以注册health
        :return:
        '''
        ''''
        # 注册 服务API
        resp = requests.post('http://{kong}/apis/'.format(kong=KONG),
                             json={'name': 'rightmanage_v1.0',
                                   'uris': '/rightmanage/v1.0',
                                   'upstream_url': 'http://{server}/rightmanage/v1.0'.format(server=SERVER)})
        print('注册 服务API', resp.text)

        resp = requests.post('http://{kong}/apis/rightmanage_v1.0/plugins'.format(kong=KONG),
                             json={"name": "jwt"})
        print('注册服务API JWT', resp.text)
        '''
        api_url = '{kong}/apis/'.format(kong=self.admin_uri)
        # 如果kong_uris有值，则需要用它注册
        api_name = base_path.replace('/','_').replace('.','_').strip('_')


        upstream_url = 'http://{upstream_name}{base_path}'.format(upstream_name=upstream_name,
                                                                   base_path=base_path)
        try:
            # 删除旧的api
            resp = requests.delete('{kong}/apis/{api_name}'.format(kong=self.admin_uri,
                                                            api_name=api_name))
            logger.info('del api(%s) %s,%s '% (api_name,resp.status_code,resp.text))
            resp = requests.post(api_url,
                                 json={'name': api_name,
                                       'uris': base_path,
                                       'upstream_url': upstream_url,
                                       'preserve_host': True})
            logger.info('注册%s服务 to kong 成功,%s '% (base_path, resp.text))
        except Exception as e:
            logger.error('注册 %s服务失败,error:%s' % (base_path, e))

            sys.exit(-1)
        if auth:
            if isinstance(auth, str):
                auth =[auth]

            if 'jwt' in auth:
                auth_data =  {"name": "jwt",
                             "config.uri_param_names": "jwt",
                             "config.claims_to_verify": "exp",
                             "config.key_claim_name": "iss",
                             "config.secret_is_base64": "false",
                             "config.cookie_names": "sessionid"
                             }

            elif 'key' in auth:
                auth_data =  {"name": "key-auth",
                             "config.key_names": "apikey"
                             }


            else:
                raise Exception('不支持的auth(%s)' % auth)

            resp = requests.post('{kong}/apis/{api_name}/plugins'.format(kong=self.admin_uri,
                                                                         api_name=api_name),
                                 json=auth_data)
            if resp.status_code != 201:
                # 在0.12.1之前的kong 不支持config.cookie_names
                if 'jwt' in auth:
                    auth_data.pop('config.cookie_names')
                    resp = requests.post('{kong}/apis/{api_name}/plugins'.format(kong=self.admin_uri,
                                                                                 api_name=api_name),
                                         json=auth_data)
            if resp.status_code == 201:
                logger.info('注册%s服务API %s 成功,%s' % (base_path,auth, resp.text))
            else:
                logger.error('注册%s服务API %s 失败,%s,%s' % (base_path,auth, resp.status_code, resp.text))

    def register_upstream(self,upstream_name,service_address,health =None,weight=100):
        '''

        :param upstream_name: monitor-srv
        :param service_host: ip:port
        :param weight: 100
        :param health: 如： ordermng/v1.0/health, realtime-srv/v1.0/health
        :return:
        '''
        ''''
        # create an upstream
        $ curl -X POST http://kong:8001/upstreams \
            --data "name=address.v1.service"

        # add two targets to the upstream
        $ curl -X POST http://kong:8001/upstreams/address.v1.service/targets \
            --data "target=192.168.101.75:80"
            --data "weight=100"
        $ curl -X POST http://kong:8001/upstreams/address.v1.service/targets \
            --data "target=192.168.100.76:80"
            --data "weight=50"

        # create a Service targeting the Blue upstream
        $ curl -X POST http://kong:8001/apis/ \
            --data "name=service-api" \
            --data "uris=/aa"
            --data "upstream_url=http://address.v1.service"
        '''
        upstream_api_url = '{kong}/upstreams/'.format(kong=self.admin_uri)
        # add upstream
        try:
            '''
            healthchecks.active.http_path - 在向目标发出HTTP GET请求时应该使用的路径。默认值是“/”。
            healthchecks.active.timeout - 用于探测的HTTP GET请求的连接超时限制。默认值是1秒。
            healthchecks.active.concurrency - 在主动健康检查中并发检查的目标数量。
            你还需要为运行的探针指定间隔的值：

            healthchecks.active.healthy.interval - 健康目标的主动健康检查间隔时间（以秒为单位）。0的值表明不执行对健康目标的主动探测。
            healthchecks.active.unhealthy.interval - 对不健康目标的主动健康检查间隔时间（以秒为单位）。0值表示不应该执行不健康目标的主动探测。
            这允许您调整主动健康检查的行为，无论您是否希望探测健康和不健康的目标在相同的时间间隔内运行，或者一个比另一个更频繁。

            最后，您需要配置Kong应该如何解释探头，通过设置健康计数器上的各种阈值，一旦到达，就会触发状态变化。计数器阈值字段是：

            healthchecks.active.healthy.successes - 在主动探测中成功的数量（由healthchecks.active.healthy.http_statuses定义）来确认目标的健康
            healthchecks.active.unhealthy.tcp_failures - 在主动探测中TCP故障的数量，以确认目标是不健康的。
            healthchecks.active.unhealthy.timeouts - 在主动探测中超时的数量，以确认目标是不健康的。
            healthchecks.active.unhealthy.http_failures - 在主动探测中出现的HTTP故障数量（由healthchecks.active.healthy.http_statuses定义）来确认目标是不健康的。
           '''
            upstream = {'name': upstream_name,
                        'healthchecks.active.http_path': health or '/',
                        'healthchecks.active.healthy.interval': 0 if health is None else 5,
                        'healthchecks.active.healthy.successes': 1,
                        'healthchecks.active.unhealthy.interval': 5,
                        'healthchecks.active.unhealthy.tcp_failures': 1,
                        'healthchecks.active.unhealthy.timeouts': 3,
                        'healthchecks.active.unhealthy.http_failures': 1
                        }
            resp = requests.post(upstream_api_url, json=upstream)
            if resp.status_code == 409:
                resp = requests.patch(upstream_api_url + upstream_name, json=upstream)
            logger.info('add %s upstream to kong 成功,%s,%s' % (upstream_name,resp.status_code,resp.text))
        except Exception as e:
            logger.error('add %s upstream失败,error:%s' % (upstream_name, e))
            sys.exit(-1)
        targets_api_url = '{kong}/upstreams/{upstream_name}/targets'.format(kong=self.admin_uri,
                                                                            upstream_name=upstream_name)
        try:
            resp = requests.post(targets_api_url,
                                 json={'target': service_address, 'weight': weight})
            logger.info('add %s target to kong 成功,%s,%s' % (upstream_name,resp.status_code,resp.text))
        except Exception as e:
            logger.error('add target for %s失败,error:%s' % (upstream_name, e))

            sys.exit(-1)