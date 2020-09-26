import redis
import urllib.request
import json
import random
import zmq
import settings
from trucoin.Verification import Verification
from trucoin.Transaction import Transaction
from trucoin.Block import Block
from collections import defaultdict
from trucoin.UDPHandler import UDPHandler
from trucoin.BlockChain import BlockChain
from trucoin.TransactionOutput import TransactionOutput
from utils import decode_redis, get_own_ip, get_own_address


class Election:
    """
        This class holds the nodes election every 30 seconds. A miner is being chosen
        from a list of primary representative.
    """
    votes_map = dict()

    def __init__(self):
        # Initialization

        self.primary_representatives = dict()
        self.blockchain = BlockChain()
        self.fund_addr = "12345"
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.redis_client.hmset('fund '+self.fund_addr, {'total fund': 00})
        self.this_node_addr = get_own_address()
        self.stakes_map = dict()
        self.verification = Verification()
        # self.load_election_fund_details()

    def load_election_fund_details(self):
        # Open Election fund details file
        f = open('electionfund.json', 'r')
        data = json.load(f)
        # Set fund address
        self.fund_addr = data["address"]

    def scan_election_fund(self):
        # Scan the blockchain to get Stakes in redis fund database
        txs = self.blockchain.get_txs_by_addr(self.fund_addr)
        # Define redis pipeline
        pipe = self.redis_client.pipeline()

        for tx in txs:
            for output in tx.outputs:
                # check if output is in fund address
                if output.address == self.fund_addr:
                    if len(tx.inputs) > 0:
                        pipe.hincrbyfloat(
                            "stakes_map", tx.inputs[0].address, output.value)
        pipe.execute()

    def get_stakes(self):
        # Get stakes from redis
        self.stakes_map = decode_redis(self.redis_client.hgetall("stakes_map"))
        print("Scanned stakes ...!")

    def elect_delegate(self):
        """ This selection of a address is done by Random Probability method 
            based on stakes one provide """

        # Electing someone to vote
        print("Electing someone ...")
        # Declaring empty variables
        total_stake = 0
        arr = []
        select = ""

        # Creating address array map based on stakes
        for key, val in self.stakes_map.items():
            total_stake += int(val)
            for i in range(0, int(val)):
                arr.append(key)

        # No selection if stakes are empty
        if total_stake == 0:
            print("Empty Stakes !!!")
            return

        # Selecting a random address from addresses list
        while True:
            select = arr[random.randint(0, total_stake-1)]
            # Reselect if it selects itself
            if (select != self.this_node_addr):
                break

        # Store own vote
        self.votes_map[self.this_node_addr] = select
        print("This node's vote is ...")
        print(select)
        print("Broadcasting this vote ...")
        # UDP broadcast function
        udphandler = UDPHandler()
        udphandler.castvote(
            {"node_addr": self.this_node_addr, "representative": select})

    """def vote_to(self):
        # Broadcast the selected node to vote
        UDPHandler.broadcastmessage(json.dumps(
            {'data': {"voter_addr": self.this_node_addr, "voted_addr": select}, 'command': 'voteto'}))
        context = zmq.Context()
        z2socket = context.socket(zmq.REQ)
        z2socket.connect("tcp://0.0.0.0:%s" % settings.BROADCAST_ZMQ_PORT)
        z2socket.send_string(json.dumps({'data': {
                             "voter_addr": self.this_node_addr, "voted_addr": select}, 'command': 'voteto'}))
        message = z2socket.recv()
        print(message)
        z2socket.close()
        return"""

    def add_vote(self, vote):
        # Add a foreign vote
        self.votes_map[vote["node_addr"]] = vote["representative"]

    def def_value(self): 
        return 0

    def delegates(self):
        # Create Delegates
        votes_count = defaultdict(self.def_value)
        print(":...:...: Votes Map :...:...:")
        print(self.votes_map)
        for key, val in self.votes_map.items():
            print(val)
            votes_count[val] += 1
        votes_count = sorted(votes_count.items(),
                             key=lambda kv: (kv[1], kv[0]))
        dels = []
        if len(votes_count) > 10:
            dels = list(reversed(list(votes_count)))[0:10]
        else:
            dels = list(reversed(list(votes_count)))
        # Returning selected Delegates
        return dels
