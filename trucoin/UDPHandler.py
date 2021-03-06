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
    """ UDP Command Handler Class """

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        # Conmmand Mapping
        self.command_mapping = {
            "castvote": self.castvote,
            "ping": self.pingpong,
            "getchainlength": self.getchainlength,
            "getblockbyheight": self.getblockbyheight,
            "getmempoollength": self.getmempoollength,
            "gettime": self.gettime,
            "getspace": self.get_disk_space,
            "gettxbymindex": self.gettxbymindex,
            "getallmtxhash": self.getallmtxhash,
            "gettxbyhash": self.gettxbyhash,
            "sendtransaction": self.sendtransaction,
            "sendblock": self.sendblock,
            "synctime": self.synctime,
            "synctx": self.synctx
        }

    @staticmethod
    def sendmessage(message, sender_ip):
        """ This method is to send message to some manual IP """

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
        """ This method is to broadcast message to all IPs """

        own_ip = get_own_ip()
        host = '0.0.0.0'
        port = settings.UDP_BROADCAST_PORT
        udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpsock.bind((host, port))
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        nodes_map = decode_redis(redis_client.hgetall("nodes_map"))
        # print(nodes_map)
        for ip_addr, raw_data in nodes_map.items():
            if ip_addr == own_ip:
                continue
            data = json.loads(raw_data)
            # print(data)
            udpsock.sendto(message.encode('utf-8'),
                           (ip_addr, int(data["receiver_port"])))
        udpsock.close()

    def command_handler(self, data):
        """ Main Command Handler """

        # If receiving a command
        if "command" in data.keys():
            if "body" in data.keys():
                # If data is present in with command
                self.command_mapping[data['command']](None, data)
            else:
                # If data is absent 
                self.command_mapping[data['command']](None, None)

        # If replying to a command
        elif "prev_command" in data.keys():
            if "body" in data.keys():
                # If data is present in previous command
                self.command_mapping[data['prev_command']](None, data)
            else:
                # If data is absent
                self.command_mapping[data['prev_command']](None, None)

    def castvote(self, request=None, response=None):
        """ Casting Vote for election """

        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        elif request is not None:
            # Processing requests 
            self.broadcastmessage(json.dumps({
                "prev_command": "castvote",
                "body": request
            }))
        elif response is not None:
            # Processing reaponse
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://127.0.0.1:%s" %
                            settings.ELECTION_ZMQ_PORT)
            print("recieving vote")
            socket.send_string(json.dumps(response["body"]))
            msg = socket.recv()
            print(msg)

    def pingpong(self, request=None, response=None):
        """ UDP ping pong """

        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        if request is not None:
            # Processing requests
            # print(request)
            self.sendmessage(json.dumps({
                "prev_command": "ping",
                "body": {"reply": "pong"}
            }), request["ip_addr"])
        if response is not None:
            # Processing reaponse
            self.sendmessage(json.dumps({
                "prev_command": "ping",
                "body": {"reply": "pong"}
            }), response["ip_addr"])

    def getchainlength(self, request=None, response=None):
        """ Get length of Blockchain """

        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        if request is not None:
            # Processing requests 
            UDPHandler.sendmessage(json.dumps({
                "command": "getchainlength",
                "body": ""
            }), request["ip_addr"])
        if response is not None:
            # Processing reaponse
            if "command" in response.keys():
                ln = self.redis_client.llen("chain")
                UDPHandler.sendmessage(json.dumps({
                    "prev_command": "getchainlength",
                    "body": ln
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
        """ Get block by height """

        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        if request is not None:
            # Processing requests 
            UDPHandler.sendmessage(json.dumps({
                "command": "getblockbyheight",
                "body": request["height"]
            }), request["ip_addr"])
        if response is not None:
            # Processing reaponse
            if "command" in response.keys():
                blk = self.redis_client.lindex('chain', response["body"]).decode("utf-8")
                UDPHandler.sendmessage(json.dumps({
                    "prev_command": "getblockbyheight",
                    "body": blk
                }), response["ip_addr"])
            elif "prev_command" in response.keys():
                context = zmq.Context()
                socket = context.socket(zmq.REQ)
                socket.connect("tcp://127.0.0.1:%s" %
                               settings.SYNC_ZMQ_PORT)
                socket.send_string(json.dumps(response))
                msg = socket.recv()
                print(msg)

    def getmempoollength(self, request=None, response=None):
        """ Get length of Mempool """

        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        if request is not None:
            # Processing requests
            UDPHandler.sendmessage(json.dumps({
                "command": "getmempoollength",
                "body": ""
            }), request["ip_addr"])
        if response is not None:
            # Processing reaponse
            if "command" in response.keys():
                mm = Mempool()
                ln = mm.get_len()
                UDPHandler.sendmessage(json.dumps({
                    "prev_command": "getmempoollength",
                    "data": ln
                }), response["ip_addr"])

    def gettxbymindex(self, request=None, response=None):
        """ Get Mempool transaction by index """

        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        if request is not None:
            # Processing requests
            UDPHandler.sendmessage(json.dumps({
                "command": "gettxbymindex",
                "body": request["index"]
            }), request["ip_addr"])
        if response is not None:
            # Processing reaponse
            if "command" in response.keys():
                mm = Mempool()
                tx = mm.get_tx_by_mindex(response["body"])
                UDPHandler.sendmessage(json.dumps({
                    "prev_command": "gettxbymindex",
                    "data": tx
                }), response["ip_addr"])

    def sendtransaction(self, request=None, response=None):
        """ Send transaction """

        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        if response is not None:
            # Processing reaponse
            if "command" in response.keys():
                mm = Mempool()
                tx = Transaction()
                mm.add_transaction(tx.from_json(response["body"]))

    def sendblock(self, request=None, response=None):
        """ Send block """
        
        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        if request is not None:
            # Processing requests
            UDPHandler.broadcastmessage(json.dumps({
                "prev_command": "sendblock",
                "body": request
            }))
        if response is not None:
            # Processing reaponse
            blkc = BlockChain()
            blkc.add_block(Block.from_json(response["body"]))
            blkc.close()

    def get_disk_space(self, request=None, response=None):
        """ Ask for disk space """

        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        if request is not None:
            # Processing requests
            UDPHandler.broadcastmessage(json.dumps({
                "command": "getspace",
                "body": {}
            }))
        if response is not None:
            # Processing reaponse
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
        """ Get all mempool transactiona by hash """
        
        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        if request is not None:
            # Processing requests
            UDPHandler.broadcastmessage(json.dumps({
                "command": "getallmtxhash"
            }))
        if response is not None:
            # Processing reaponse
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
        """ Get transaction by hash """

        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        if request is not None:
            # Processing requests
            UDPHandler.sendmessage(json.dumps({
                "hash": request["hash"]
            }), request["ip_addr"], request["receiver_port"])
        elif response is not None:
            # Processing reaponse
            mempool = Mempool()
            mempool.add_transaction(
                Transaction.from_json(json.loads(response)["tx"]))

    def synctx(self, request=None, response=None):
        """ Sync transaction command """

        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        if request is not None:
            # Processing requests
            UDPHandler.sendmessage(json.dumps({
                "command": "synctx",
                "body": request["body"]
            }), request["ip_addr"])
        elif response is not None:
            # Processing reaponse
            mempool = Mempool()
            mempool.sync_transaction(json.loads(response["body"]))

    def synctime(self, request=None, response=None):
        """ Sync time command """

        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        if request is not None:
            # Processing requests
            print(request['ip_addr'])
            UDPHandler.sendmessage(json.dumps({
                "command": "synctime",
                "body":{"timestamp": time.time()}
            }), request["ip_addr"])
        if response is not None:
            # Processing reaponse
            if "prev_command" in response.keys():
                ts=TimeServer()
                redis_client = redis.Redis(host='localhost', port=6379, db=0)
                current_timestamp = time.time()
                print((current_timestamp - int(float(response['body']["timestamp"]))) / 2)
                redis_client.set(
                    "delay_time", (int(current_timestamp) - int(float(response['body']["timestamp"]))) / 2)
                ts.set_time(int(float(response["body"]["time"])) +
                        int(float(redis_client.get("delay_time").decode("ascii"))))
            else:
                UDPHandler.sendmessage(json.dumps({
                "prev_command":"synctime",
                "body":{"timestamp":response['body']['timestamp'],'time':time.time()}
                }), response["ip_addr"])
                

    def gettime(self, request=None, response=None):
        """ Get time """

        ts = TimeServer()
        if request is None and response is None:
            # If no data is being passed on by command handler
            pass
        if request is not None:
            # Processing requests
            UDPHandler.sendmessage(json.dumps({
                "command":"gettime"
            }),request['ip_addr'])
        if response is not None:
            # Processing reaponse
            if "prev_command" in response.keys():
                raw = json.loads(response)
                redis_client = redis.Redis(host='localhost', port=6379, db=0)
                ts.set_time(int(float(response["body"]["timestamp"])) +
                            int(float(redis_client.get("delay_time").decode("ascii"))))
            else:
                UDPHandler.sendmessage(json.dumps({
                    "prev_command":"gettime",
                    "body":{"timestamp":time.time()}
                }),request['ip_addr'])


        
  