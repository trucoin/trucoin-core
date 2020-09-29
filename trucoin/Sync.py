import time 
import socket
import settings
from utils import handle_network_error,get_own_ip
import urllib
import json
from urllib.error import URLError
from trucoin.UDPHandler import UDPHandler
class Sync:

    def sync_server(self):
        print("Sycing node with nodes")
        message={
            "command":"echo",
            "time":time.time()
        }
        udp = UDPHandler()
        ip=self.fetch_nodes()
        if ip:
            udp.sendmessage(message,ip)

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


  