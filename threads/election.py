import urllib.request
import settings
from trucoin.BlockChain import BlockChain
from trucoin.Verification import Verification
from trucoin.Transaction import Transaction
from trucoin.Election import Election
from trucoin.Block import Block
from trucoin.Node import Node
import json
from collections import defaultdict
import random
import zmq
import time
import redis
import threading
import urllib.request
import settings
from trucoin.UDPHandler import UDPHandler
import utils
from trucoin.Mining import Mining

def bestblock(merkle_roots=[]):
    # Function to get the most common block
    key_value = dict()
    max = []
    for i, merkle_root in enumerate(merkle_roots):
        if not merkle_root in key_value.keys():
            key_value[merkle_root] = 1
        else:
            key_value[merkle_root] += 1

    for key in key_value.keys():
        max.append(key_value[key])
        max.sort(reverse=True)
    for key in key_value.keys():
        if key_value[key] == max[0]:
            print(key)
            return key


def worker():
    # Initializing Election Class
    elec = Election()
    # Scan the election fund top get stakes
    elec.scan_election_fund()
    # Get stakes
    elec.get_stakes()
    # Select your vote
    elec.elect_delegate()
    print("Vote sent and waiting for other's votes ...")
    # ZMQ server to recieve the other node's votes
    context = zmq.Context()
    zsocket = context.socket(zmq.REP)
    zsocket.bind("tcp://127.0.0.1:%s" % settings.ELECTION_ZMQ_PORT)
    # Using ZMQ Poller
    zpoll = zmq.Poller()
    zpoll.register(zsocket)
    start_timestamp = time.time()
    # Time to wait for others's votes
    while time.time() - start_timestamp < 10:
        events = dict(zpoll.poll(1))
        for key in events:
            vote = json.loads(key.recv_string())
            elec.add_vote(vote)
            zsocket.send_string("Got some node's vote!")
    zpoll.unregister(zsocket)
    zsocket.close()
    context.destroy()
    # Compute and return the list of delegates
    return elec.delegates()

def mining():
    print("Into the mining process")
    # Initializing Election Class
    elec = Election()
    # Do not make a block if mempool is empty
    # if elec.redis_client.llen("mempool") == 0:
    #     print("No block made! Mempool is empty!")
    #     return
    # Transaction verification 
    # Initializing Block Class
    blk = Block()
    # Create Coinbase Transaction
    blk.create_coinbase_transaction()
    # Connect to Previous Block
    blk.add_previous_block()
    # Scan Mempool
    vd = True
    for i in range(0, elec.redis_client.llen("mempool")):
        # Get Transaction
        tx = elec.redis_client.lindex('mempool', i).decode('utf-8')
        if tx == None:
            # Exit if tx is None
            break
        # Get tx verification verdict 
        # verify_verdict = elec.verification.verify_tx(tx)
        # if verify_verdict == "verified":
        #     # Sending data to block
        #     blk.add_transaction(tx)
        # else:
        #     vd = False
        #     print("Some Transaction Verification Failed! Aborting Mining ...")
        #     break
    # If Tx Verification Fails
    if vd == False:
        print("Mining Aborted!")
        return 
    # create block
    blk.compute_hash()
    blk.calculate_merkle_root()
    block = blk
    # add block
    blkChain = BlockChain()
    blkChain.add_block(block)
    print("Block added to this Node's blockchain!")
    # check
    # full Blockchain verify
    # full_verify_message = elec.verification.full_chain_verify()
    # if full_verify_message == "verified":
        # braodcast the block you made
    print("Broadcasting block made by this node ...")
    udphandler = UDPHandler()
    udphandler.sendblock(block.to_json())
    # else:
    #     return

def electionworker():
    # Run the election Process
    elec = Election()
    # Get Delegates
    dels = worker()
    # Print Delegates
    print("The delegates are :")
    print(dels)
    # Variable to store if this node is delegate or not
    is_del = False
    # Check if this node is del or non-del
    for k, v in dels:
        if k == elec.this_node_addr:
            print("I am a delegate")
            is_del = True   
    if is_del == False:
        # If this node is not a delegate
        print("running as non-del")
        add_block_nondel()
    else:
        # If this node is a delegate
        print("Starting to mine")
        mining()
    # while True:
    #     mining = Mining()
    #     block = mining.create_block()
    #     if block is not None:
    #         UDPHandler.broadcastmessage(json.dumps({
    #             "command": "sendblock",
    #             "body": block.to_json()
    #         }))
    #     time.sleep(30)

def add_block_nondel():
    # Running as Non delegate
    print("Waiting to get blocks made by Delegates :")
    # ZMQ to recieve block got at UDP Port
    context = zmq.Context()
    zsocket = context.socket(zmq.REP)
    zsocket.bind("tcp://127.0.0.1:%s" % settings.ELECTION_ZMQ_PORT)
    # ZMQ Poller
    zpoll = zmq.Poller()
    zpoll.register(zsocket)
    start_timestamp = time.time()
    # Storing all recieved blocks
    all_blocks = []
    # Time to wait for recieving blocks
    while time.time() - start_timestamp < 3:
        events = dict(zpoll.poll(1))
        for key in events:
            block = json.loads(key.recv_string())
            all_blocks.append(block)
            zsocket.send_string("Got a block!")
    zpoll.unregister(zsocket)
    zsocket.close()
    context.destroy()
    print("Recieved " + str(len(all_blocks)) + " Blocks!")
    # Get most common and add to chain
    if len(all_blocks) > 0:
        mr = []
        for blk in all_blocks:
            print("Getting the most common Block ...")
            mr.append(blk["merkle_root"])
        # Add the most common block
        blkc = BlockChain()
        Mblock = bestblock(mr)
        blkc.add_block(Mblock)
        # Initializing Election Class
        elec = Election()
        # full Blockchain verify
        # elec.verification.full_chain_verify()

def memsync():
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
    ask = ""
    for i in range(0,length):
        if ip_list[i] == ip_address:
            if i == (length - 1):
                ask = ip_list[0]
            else:
                ask = ip_list[i+1]

    print("Starting mempool transaction sync ...")
    # UDP command to ask from ask 
    


def run_thread():
    # Main function to run threads
    Node()
    # run mempool sync
    memsync()
    print("Starting Election/Mining rocess")
    while True:
        t = threading.Thread(target=electionworker)
        t.start()
        t.join()
