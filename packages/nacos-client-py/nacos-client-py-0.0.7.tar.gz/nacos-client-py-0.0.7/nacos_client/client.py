import logging
import os
import random
import socket
import threading
import time
from functools import wraps

import nacos
import requests

logging.basicConfig()
logger = logging.getLogger(__name__)


class NacosClientException(Exception):
    pass


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    finally:
        s.close()


class NacosClient:
    debug = False

    def set_debugging(self):
        if not self.debug:
            global logger
            logger.info('debuging...')
            logger = logging.getLogger("nacos_client")
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s:%(message)s"))
            logger.addHandler(handler)
            logger.setLevel(level=logging.DEBUG)
            self.debug = True
            self.client.set_debugging()

    def __init__(self, server_addresses, namespace=None, username=None, password=None):
        self.server_address = server_addresses
        self.namespace = namespace
        self.client = nacos.NacosClient(server_addresses, namespace=namespace, username=username, password=password)
        self.service_dict = {}

    def register(self, service_name, ip, port, cluster_name='DEFAULT', weight=1, metadata=None):
        cluster, group = os.environ.get('WCloud_Cluster'), os.environ.get('WCloud_Cluster_Group')
        if cluster and group:
            cluster_name = f'{cluster}__{group}'
        logger.info("[register] service_name:%s, ip:%s, port:%s, cluster_name:%s, weight:%s" % (
            service_name, ip, port, cluster_name, weight))
        try:
            re = self.client.add_naming_instance(service_name, ip, port, cluster_name=cluster_name, weight=weight)
            logger.info(f"[register] success! {re}")
            thread = threading.Thread(target=self.health_check, args=(service_name, ip, port, cluster_name, weight, metadata))
            thread.start()
        except:
            logging.error("[regiser] failed!", exc_info=True)

    def health_check(self, service_name, ip, port, cluster_name, weight, metadata):
        logger.info("[health_check] service_name:%s, ip:%s, port:%s, cluster_name:%s, weight:%s" % (
            service_name, ip, port, cluster_name, weight))
        while True:
            time.sleep(3)
            try:
                if metadata is None:
                    metadata = {}
                result = self.client.send_heartbeat(service_name, ip, port, cluster_name, weight, metadata=metadata)
                if result.get('code') != 10200:
                    logger.info(f'[send_heartbeat] failed! register again')
                    self.register(service_name, ip, port, cluster_name, weight)
                    break
            except:
                logging.error("[send_heartbeat] error!", exc_info=True)

    def get_service_host(self, service_name, clusters=None, group_name=None):
        logger.info("[get_service_host] service_name:%s, clusters:%s, group_name:%s" % (service_name, clusters, group_name))
        if not self.service_dict.get(service_name):
            config_dic = self.client.list_naming_instance(
                service_name, clusters, namespace_id=self.namespace, group_name=group_name, healthy_only=True)
            hosts = config_dic.get("hosts")
            if not hosts:
                logger.error(f'[get_service_host] no service avaliable! service: {service_name}')
                return None
            self.service_dict[service_name] = [f"{i['ip']}:{i['port']}" for i in hosts]
        return random.choice(self.service_dict[service_name])

    def request(self, service, path, method, clusters=None, group_name=None, https=False):
        def decorate(func):
            @wraps(func)
            def wrapper(**kwargs):
                host = self.get_service_host(service, clusters=clusters, group_name=group_name)
                if not host:
                    raise NacosClientException(f'no service avaliable! service: {service}')
                url = f'{"https" if https else "http"}://{host}{path}'
                return requests.request(method, url, **kwargs)
            return wrapper
        return decorate
