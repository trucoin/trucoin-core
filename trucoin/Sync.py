import time 
import socket
import settings
from utils import handle_network_error,get_own_ip
import urllib
import json
from urllib.error import URLError
from trucoin.UDPHandler import UDPHandler
import redis
class Sync:

    def sync_server(self,ip=None):
        ip=self.fetch_nodes()
        if ip is not None:
            udp = UDPHandler()
            udp.synctime(json.loads({'ip_addr':ip}))
            redis_client = redis.Redis(host='localhost', port=6379, db=0)
            while not 'delay_time' in redis_client.keys('*'):
                time.sleep(2)
                print("syncing time")
            print('time synced')
        print("server synced")

    def fetch_nodes(self):
        own_ip = get_own_ip()
        for url in settings.DNS_SERVERS:
            try:
                response = urllib.request.urlopen(url + "/get_nodes")
            except URLError as e:
                handle_network_error(e)
            else:
                raw = response.read()
                result = json.loads(raw.decode("utf-8"))
                for value in result['nodes']:
                    if value['ip_addr'] == own_ip or value['ip_addr'] == settings.EXPLORER_IP:
                        continue
                    return value['ip_addr']
                    break


  