# all imports
import socket
import selectors
import types
import os
import redis
import urllib
import urllib.request
import settings
import json
import ast
import multiprocessing 
import time
from threads.receiver import *  
from threads.rpc import rpc_receive
from threads.election import run_thread
from trucoin.Address import Address
from threads.storage import start
from trucoin.Node import Node
from trucoin.Sync import Sync

# Defining host and port to run the main server on
host = '0.0.0.0'
port = 8080
sync = Sync()
def cpu_count():
    """ Returns CPU count and software compatibility """
    cpucount = os.cpu_count()
    print("total cpu cores in the system=",cpucount)
    if cpucount < 2:
        print("this version of software can't run on your system")
        exit()

def run_threads():
    """ running multiple processes """
    # Receiver
    receiver=multiprocessing.Process(target=broadcast_receive)
    receiver.start()

    sync.sync_server()
    # RPC
    rpc=multiprocessing.Process(target=rpc_receive)
    rpc.start()

    
    # Election & Mining
    election_process = multiprocessing.Process(target=run_thread)
    election_process.start()
    # Storage 
    storage_process = multiprocessing.Process(target=start)
    storage_process.start()

def node_start():
    """ root method """

    # Storage folder creation
    curr_dir = os.getcwd()
    print("Your current working directory" + curr_dir)
    stx_dir = curr_dir + "/storage/"
    print("Path of storage folder" + stx_dir)
    if not os.path.exists(stx_dir):
        os.makedirs(stx_dir)
    # initialize node with DNS
    node = Node()
    # get cpu data
    cpu_count()
    sync.chainsync()
    # start processes
    run_threads()
    


if __name__ == '__main__':
    node_start()

        


