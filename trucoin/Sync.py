import time 
import socket
import settings
from utils import handle_network_error,get_own_ip
import urllib
import json
from urllib.error import URLError
class Sync:

    def sync_server(self):
        print("Sycing node with nodes")
        message={
            "command":"echo",
            "time":time.time()
        }
        host = '0.0.0.0'
        port = settings.UDP_BROADCAST_PORT
        udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpsock.bind((host, port))
        ip=self.fetch_nodes()
        if ip:
            udpsock.sendto(message.encode('utf-8'), (ip, settings.UDP_RECEIVER_PORT))
            sock= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, settings.UDP_RECEIVER_PORT))  
            data, client_address = self.sock.recvfrom(4096) 

        udpsock.close()
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


  