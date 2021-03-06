import json
import redis
from trucoin.Mempool import Mempool
from trucoin.Transaction import Transaction
from trucoin.Address import Address
from trucoin.BlockChain import BlockChain
from trucoin.UDPHandler import UDPHandler


class RPC:
    # check for type of data sent
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.command_mapping = {
            'addtransaction': self.addtransaction,
            'getlastblock': self.getlastblock,
            'getaddressbalance': self.getaddressbalance,
            'getblockbyheight': self.getblockbyheight,
            'gettxbyhash': self.gettxbyhash,
            'getnodeinfo': self.getnodeinfo,
            'getstakes': self.getstakes,
            'gettxsbyaddress': self.gettxsbyaddress,
            'ping': self.pingpong,
            "getchainlength": self.getchainlength,
            "getallutxobyaddress": self.getallutxobyaddress,
            "getblockbyhash": self.getblockbyhash
        }

    def handlecommand(self, data):
        if data["command"] in self.command_mapping.keys():
            if "parameters" in data.keys():
                return self.command_mapping[data["command"]](data["parameters"])
            elif "body" in data.keys():
                return self.command_mapping[data["command"]](data["body"])
            else:
                return self.command_mapping[data["command"]]()
        else:
            return json.dumps({
                "error": "RPC Command doesn't exists"
            })

    def addtransaction(self, data):
        tx = Transaction.from_json({
            "block": "Mempool",
            **data
        })
        mempool = Mempool()
        print("adding to mempool")
        mempool.add_transaction(tx)
        
        UDPHandler.broadcastmessage(json.dumps({
            "command": "sendtransaction",
            "body": tx.to_json()
        }))
        return json.dumps({
            "status": "ok"
        })

    def getlastblock(self, data=None):
        return self.redis_client.lindex('chain', -1).decode("utf-8")

    def getaddressbalance(self, data=None):
        blkc = BlockChain()
        balance = blkc.final_addr_balance(data)
        blkc.close()
        return json.dumps({
            "balance": balance
        })

    def getblockbyheight(self, data=None):
        blkc = BlockChain()
        block = blkc.get_block(data)
        if block is not None:
            return json.dumps({
                "block": block.to_json()
            })
        else:
            return json.dumps({
                "error": "Block not found at this height"
            })

    def gettxsbyaddress(self, data=None):
        blkc = BlockChain()
        txs = [tx.to_json() for tx in blkc.get_txs_by_addr(data)]
        blkc.close()
        return json.dumps({
            "txs": txs
        })

    def getnodeinfo(self, data=None):
        with open("node_data.json", 'r') as json_file:
            my_node = json.load(json_file)
        return json.dumps(my_node)

    def getstakes(self, data=None):
        fetch_stakes_bytes = self.redis_client.hgetall('fund '+self.fund_addr)
        fetch_stakes = {y.decode('ascii'): fetch_stakes_bytes.get(
            y).decode('ascii') for y in fetch_stakes_bytes.keys()}
        self.stakes = fetch_stakes
        return fetch_stakes

    def gettxbyhash(self, data=None):
        blkc = BlockChain()
        tx = blkc.get_tx_by_hash(data)
        blkc.close()

        if tx is not None:
            return json.dumps({
                "tx": tx.to_json()
            })
        else:
            return json.dumps({
                "error": "Transaction not found"
            })

    def pingpong(self, data=None):
        return json.dumps({
            "reply": "pong"
        })

    def getchainlength(self, data=None):
        return json.dumps({
            "length": self.redis_client.llen("chain")
        })

    def getallutxobyaddress(self, data=None):
        blkc = BlockChain()
        utxos_tuple = blkc.get_utxos_by_addr(data)
        response = [{"tx": utxo[0], "index": utxo[1], "amount": utxo[2]}
                    for utxo in utxos_tuple]
        blkc.close()
        return json.dumps({
            "utxos": response
        })

    def getblockbyhash(self, data=None):
        blkc = BlockChain()
        block = blkc.get_block_by_hash(data)

        if block is not None:
            return json.dumps({
                "block": block.to_json()
            })
        else:
            return json.dumps({
                "error": "Block not found"
            })