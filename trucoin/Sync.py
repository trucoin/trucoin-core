import time 
import zmq
import socket
import random
import settings
import utils
from utils import handle_network_error,get_own_ip
import urllib
import json
from urllib.error import URLError
from trucoin.UDPHandler import UDPHandler
from trucoin.BlockChain import BlockChain
from trucoin.Verification import Verification
import redis

class Sync:

    def sync_server(self,ip=None):
        ip=self.fetch_nodes()
        if ip is not None:
            udp = UDPHandler()
            udp.synctime({"ip_addr":ip})
            redis_client = redis.Redis(host='localhost', port=6379, db=0)
            while  redis_client.exists('delay_time'):
                time.sleep(2)
                print("syncing time")
                if redis_client.exists('delay_time'):
                    break
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
                    if value['ip_addr'] == own_ip or value['ip_addr'] == settings.EXPLORER_IP[0]:
                        continue
                    else:
                        return value['ip_addr']
                    break
    
    def chainsync(self):
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        ip_list = []
        nodes_map = utils.decode_redis(redis_client.hgetall("nodes_map"))
        
        for ip_addr, raw_data in nodes_map.items():
            ip_list.append(ip_addr)

        # IP chosing method is under development!
        ip = random.choice(ip_list)

        udp = UDPHandler()
        
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        udp.getchainlength({"ip_addr": ip})
        socket.connect("tcp://127.0.0.1:%s" %
                                settings.SYNC_ZMQ_PORT)
        res = json.loads(socket.recv_string())
        length = res["data"]
        socket.send_string("Recieved Chain Length")
        socket.close()

        mylen = redis_client.llen("chain")

        if mylen == 0:
            for i in range(0, length):
                udp.getblockbyheight({"height": i, "ip_addr": ip})
                socket.connect("tcp://127.0.0.1:%s" %
                                    settings.SYNC_ZMQ_PORT)
                res = json.loads(socket.recv_string())
                socket.send_string("Recieved a block of the chain!!!")
                socket.close()
                blchain = Blockchain()
                blchain.add_block(res["data"])
            # chain verification
            verf = Verification()
            msg = verf.full_chain_verify()
            if msg != "verified":
                return self.chainsync()
        elif mylen > length:
            return self.chainsync()
        elif mylen == length:
            return
        elif mylen < length:
            for i in range(mylen, length):
                udp.getblockbyheight(({"height": i, "ip_addr": ip}))
                socket.connect("tcp://127.0.0.1:%s" %
                                    settings.SYNC_ZMQ_PORT)
                res = json.loads(socket.recv_string())
                socket.send_string("Recieved a block of the chain!!!")
                socket.close()
                blchain = BlockChain()
                blchain.add_block(res["data"])
            # chain verification
            verf = Verification()
            msg = verf.full_chain_verify()
            if msg != "verified":
                return self.chainsync()

    def memsync(self):
        ip_address = utils.get_own_ip()
        print("Mempool sync started ...")
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        ip_list = []
        ip_list.append(ip_address)

        nodes_map = utils.decode_redis(redis_client.hgetall("nodes_map"))
        
        for ip_addr, raw_data in nodes_map.items():
            if ip_addr == ip_address:
                continue
            else:
                ip_list.append(ip_addr)

        print("Nodes list : " + str(ip_list))

        ip_list.sort()
        length = len(ip_list)
        send = ""

        if length == 0:
            print("NO NODES ACTIVE TO SYNC WITH!!!")
            return

        for i in range(0,length):
            if ip_list[i] == ip_address:
                if i == 0:
                    send = ip_list[-1]
                else:
                    send = ip_list[i-1]

        print("Starting mempool transaction sync ...")
        # UDP command to send txs to prev addr
        i = 0
        while True:
            tx = redis_client.lindex("mempool", i)
            if tx == None:
                break
            udp = UDPHandler()
            print("Sending transaction for sync " + str(i) + "....")
            udp.synctx(({
                "body": tx.decode(),
                "ip_addr": send
            }))
            i = i + 1

        time.sleep(1)
        print("Mempool sync finished!!!")


    