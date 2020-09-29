from trucoin.Transaction import Transaction
from trucoin.Mempool import Mempool
import zmq
import os
import shutil
import json
import settings
import socket
import redis
import time
from trucoin.TimeServer import TimeServer
from trucoin.BlockChain import BlockChain
from trucoin.Block import Block
from utils import decode_redis, get_own_ip


class UDPHandler:

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.command_mapping = {
            "castvote": self.castvote,
            "getchainlength": self.getchainlength,
            "getblockbyheight": self.getblockbyheight,
            "getmempoollength": self.getmempoollength,
            "gettxbymindex": self.gettxbymindex,
            "sendtransaction": self.sendtransaction,
            "sendblock": self.sendblock,
            "getallmtxhash": self.getallmtxhash,
            "gettxbyhash": self.gettxbyhash,
            "synctime": self.synctime,
            "gettime": self.gettime,
            "ping": self.pingpong,
            "getspace": self.get_disk_space,
            "synctx": self.synctx
        }

    @staticmethod
    def sendmessage(message, sender_ip):
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        raw = redis_client.hget("nodes_map", sender_ip)
        sender_port = settings.UDP_RECEIVER_PORT
        if raw is not None:
            sender_port = json.loads(raw.decode("utf-8"))["receiver_port"]
        host = '0.0.0.0'
        port = settings.UDP_BROADCAST_PORT
        udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpsock.bind((host, port))
        udpsock.sendto(message.encode('utf-8'), (sender_ip, int(sender_port)))
        udpsock.close()

    @staticmethod
    def broadcastmessage(message):
        own_ip = get_own_ip()
        host = '0.0.0.0'
        port = settings.UDP_BROADCAST_PORT
        udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpsock.bind((host, port))
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        nodes_map = decode_redis(redis_client.hgetall("nodes_map"))
        print(nodes_map)
        for ip_addr, raw_data in nodes_map.items():
            if ip_addr == own_ip:
                continue
            data = json.loads(raw_data)
            print(data)
            udpsock.sendto(message.encode('utf-8'),
                           (ip_addr, int(data["receiver_port"])))
        udpsock.close()

    def command_handler(self, data):
        if "command" in data.keys():
            if "body" in data.keys():
                self.command_mapping[data['command']](None, data)
            else:
                self.command_mapping[data['command']](None, None)
        elif "prev_command" in data.keys():
            if "body" in data.keys():
                self.command_mapping[data['prev_command']](None, data)
            else:
                self.command_mapping[data['prev_command']](None, None)

    def castvote(self, request=None, response=None):
        if request is not None:
            self.broadcastmessage(json.dumps({
                "prev_command": "castvote",
                "body": request
            }))
        if response is not None:
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://127.0.0.1:%s" %
                            settings.ELECTION_ZMQ_PORT)
            print("recieving vote")
            socket.send_string(json.dumps(response["body"]))
            msg = socket.recv()
            print(msg)

    def getchainlength(self, request=None, response=None):
        if request is not None:
            UDPHandler.sendmessage(json.dumps({
                "command": "getchainlength",
                "body": ""
            }), request["ip_addr"])
        else:
            if "command" in response.keys():
                ln = self.redis_client.llen("chain")
                UDPHandler.sendmessage(json.dumps({
                    "prev_command": "getchainlength",
                    "data": ln
                }), response["ip_addr"])
            elif "prev_command" in response.keys():
                context = zmq.Context()
                socket = context.socket(zmq.REQ)
                socket.connect("tcp://127.0.0.1:%s" %
                               settings.SYNC_ZMQ_PORT)
                socket.send_string(json.dumps(response))
                msg = socket.recv()
                print(msg)


    def getblockbyheight(self, request=None, response=None):
        if request is not None:
            UDPHandler.sendmessage(json.dumps({
                "command": "getblockbyheight",
                "height": request["height"]
            }), request["ip_addr"])
        else:
            if "command" in response.keys():
                blk = self.redis_client.lindex('chain', response["height"]).decode("utf-8")
                UDPHandler.sendmessage(json.dumps({
                    "prev_command": "getblockbyheight",
                    "data": blk
                }), response["ip_addr"])
            elif "prev_command" in response.keys():
                context = zmq.Context()
                socket = context.socket(zmq.REQ)
                socket.connect("tcp://127.0.0.1:%s" %
                               settings.SYNC_ZMQ_PORT)
                socket.send_string(json.dumps(response))
                msg = socket.recv()
                print(msg)

    def getmempoollength(self, data):
        mm = Mempool()
        return mm.get_len()

    def gettxbymindex(self, data):
        mm = Mempool()
        return mm.get_tx_by_mindex(data["body"].index)

    def sendtransaction(self, request=None, response=None):
        # tx = Transaction.from_json(data['body'])
        # UDPHandler.broadcastmessage(json.dumps(tx.to_json()))
        pass

    def sendblock(self, request=None, response=None):
        print(request)
        if request is not None:
            UDPHandler.broadcastmessage(json.dumps({
                "prev_command": "sendblock",
                "body": request
            }))
        if response is not None:
            blkc = BlockChain()
            blkc.add_block(Block.from_json(response["body"]))
            blkc.close()

    def get_disk_space(self, request=None, response=None):
        if request is not None:
            UDPHandler.broadcastmessage(json.dumps({
                "command": "getspace",
                "body": {}
            }))
        if response is not None:
            if "command" in response.keys():
                curr_dir = os.getcwd()
                print(curr_dir)
                stats = shutil.disk_usage(curr_dir)
                print("Your free space in mbs: ")
                print(stats.free * 0.00000095367432)
                UDPHandler.sendmessage(json.dumps({
                    "prev_command": "get_space",
                    "data": stats.free
                }), response["ip_addr"])
            elif "prev_command" in response.keys():
                context = zmq.Context()
                socket = context.socket(zmq.REQ)
                socket.connect("tcp://127.0.0.1:%s" %
                               settings.STORAGE_ZMQ_PORT)
                socket.send_string(json.dumps(response))
                msg = socket.recv()
                print(msg)

    def getallmtxhash(self, request=None, response=None):
        if response is None:
            UDPHandler.broadcastmessage(json.dumps({
                "command": "getallmtxhash"
            }))
        else:
            redis_client = redis.Redis(host='localhost', port=6379, db=0)
            local_tx_hashes: set = set()
            remote_tx_hashes: set = set()

            for tx in redis_client.lrange("mempool", 0, -1):
                local_tx_hashes.add(
                    Transaction.from_json(tx.decode("utf-8")).hash)

            response_data = json.loads(response)
            for tx in response_data["hashes"]:
                remote_tx_hashes.add(tx)

            remote_tx_hashes.difference_update(local_tx_hashes)

            receiver_port = settings.UDP_RECEIVER_PORT
            for raw in redis_client.lrange("nodes", 0, -1):
                info = json.loads(raw.decode("utf-8"))
                if info["ip_addr"] == response_data["ip_addr"]:
                    receiver_port = info["receiver_port"]

            for tx_hash in remote_tx_hashes:
                self.gettxbyhash({
                    "hash": tx_hash,
                    "ip_addr": response_data["ip_addr"],
                    "receiver_port": receiver_port
                })

    def gettxbyhash(self, request=None, response=None):
        if request is not None:
            UDPHandler.sendmessage(json.dumps({
                "hash": request["hash"]
            }), request["ip_addr"], request["receiver_port"])
        elif response is not None:
            mempool = Mempool()
            mempool.add_transaction(
                Transaction.from_json(json.loads(response)["tx"]))

    def synctx(self, request=None, response=None):
        if response is None:
            UDPHandler.sendmessage(json.dumps({
                "command": "synctx",
                "tx": request["body"]
            }), request["ip_addr"])
        else:
            mempool = Mempool()
            mempool.sync_transaction(Transaction.from_json(json.loads(response)["tx"]))

    def synctime(self, request=None, response=None):
        if response is None:
            print(request['ip_addr'])
            UDPHandler.sendmessage(json.dumps({
                "command": "synctime",
                "body":{"timestamp": time.time()}
            }), request["ip_addr"])
        else:
            if "prev_command" in response.keys():
                ts=TimeServer()
                redis_client = redis.Redis(host='localhost', port=6379, db=0)
                current_timestamp = time.time()
                print((current_timestamp - int(float(response['body']["timestamp"]))) / 2)
                redis_client.set(
                    "delay_time", (int(current_timestamp) - int(float(response['body']["timestamp"]))) / 2)
                ts.set_time(int(float(response["body"]["timestamp"])) +
                        int(float(redis_client.get("delay_time").decode("ascii"))))
                
            else:
                UDPHandler.sendmessage(json.dumps({
                "prev_command":"synctime",
                "body":{"timestamp":response['body']['timestamp']}
                }), response["ip_addr"])
            

    def gettime(self, request=None, response=None):
        ts = TimeServer()
        if response is not None:
            raw = json.loads(response)
            redis_client = redis.Redis(host='localhost', port=6379, db=0)
            ts.set_time(int(float(response["body"]["timestamp"])) +
                        int(float(redis_client.get("delay_time").decode("ascii"))))
            

    def pingpong(self, request=None, response=None):
        if response is not None:
            self.sendmessage(json.dumps({
                "prev_command": "ping",
                "body": {"reply": "pong"}
            }), response["ip_addr"])
        elif request is not None:
            print(request)
            self.sendmessage(json.dumps({
                "prev_command": "ping",
                "body": {"reply": "pong"}
            }), request["ip_addr"])
  