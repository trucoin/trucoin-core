import socket
import os
import zmq
import settings 
import hashlib
import math
import time
import redis
import threading
import json
import pickle5 as pickle
from trucoin.StorageTx import StorageTx
from trucoin.Mempool import Mempool
from trucoin.UDPHandler import UDPHandler


SERVER_HOST = settings.NODE_IP
SERVER_PORT = settings.FILE_RECV_PORT

BUFFER_SIZE = 1024
SEPARATOR = "<SEPARATOR>"

def start():
    s = socket.socket()
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
    t = threading.Thread(target=thread(s))
    t.start()
    t2 = threading.Thread(target=thread(s))
    t2.start()
    t.join()
    t2.join()

def thread(s):
    client_socket, address = s.accept() 
    print(f"[+] {address} is connected.")
    received = pickle.loads(client_socket.recv())
    filename = received["file_name"]
    filesize = received["filesize"] 
    filetype = received["filetype"]
    filehash = received["filehash"]
    fileaddr = received["fileaddr"]

    # filename, filesize, filetype, filehash, fileaddr = received.split(SEPARATOR)
    print(filetype)
    print(fileaddr)
    if filetype == "temp":
        filename = os.path.basename(settings.TEMP_STORAGE_PATH + filename)
    else:
        filename = os.path.basename(settings.STORAGE_PATH + filename)
    filesize = int(filesize)

    with open(filename, "wb") as f:
        while True:
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:    
                break
            f.write(bytes_read)

    if filetype == "temp":
        # split and broadcast
        # No. of splits to be made --> n
        print(fileaddr)
        key, val = file_split(filename)
        file_send(key, filehash, fileaddr, filename, val)
        client_socket.close()
        
    else:
        client_socket.close()

def file_split(filename):
    file_list = []
    filesize = os.path.getsize(filename)
    part_filename = hashlib.sha256(filename.encode('utf-8')).hexdigest()

    # broadcast msg to give size to all nodes
    udp = UDPHandler()
    udp.get_disk_space({})

    # get all node's free space
    ips = []
    context = zmq.Context()
    zsocket = context.socket(zmq.REP)
    zsocket.bind("tcp://127.0.0.1:%s" % settings.STORAGE_ZMQ_PORT)
    zpoll = zmq.Poller()
    zpoll.register(zsocket)
    start_timestamp = time.time()
    while time.time() - start_timestamp < 8:
        events = dict(zpoll.poll(1))
        for key in events:
            strecv = json.loads(key.recv_string())
            key.send_string("recieved your free space")
            if strecv["data"] > filesize:
                # add ip to array
                ips.append(strecv["ip_addr"])
            zsocket.send_string("got someone to store")
    zpoll.unregister(zsocket)
    zsocket.close()
    context.destroy()

    # size of ips
    n = len(ips)

    SPLIT_SIZE = math.ceil(filesize / n)
    with open(filename, "rb") as f:
        i = 0
        while True:
            bytes_read = f.read(SPLIT_SIZE)
            if not bytes_read:
                break
            # hash = hashlib.sha256(json.dumps(bytes_read).encode("utf-8")).hexdigest()
            file_list.append(bytes_read)
            i = i + 1
    
    for i in range(0,n):
        file_n = settings.TEMP_STORAGE_PATH + part_filename + str(i)
        with open(file_n, "wb") as f:
            f.write(file_list[i])

    os.remove(filename)
    return {n: ips}

def file_send(n, filehash, fileaddr, file_name, ips):
    stx = StorageTx()
    mem = Mempool()
    udp = UDPHandler()
    print(fileaddr)
    stx.add_input(filehash, fileaddr)
    part_filename = hashlib.sha256(file_name.encode('utf-8')).hexdigest()

    recv_hosts = ips
    for i in range(0,n):
        host = recv_hosts[i]
        port = 5001

        filename = settings.TEMP_STORAGE_PATH + part_filename + str(i)
        filesize = math.ceil(os.path.getsize(filename))
        filetype = "non-temp"
        
        send = socket.socket()
        print(f"[+] Connecting to {host}:{port}")
        send.connect((host, port))
        print("[+] Connected.")
        
        info = {
            "filename" : filename,
            "filesize" : filesize,
            "filetype" : filetype,
            "filehash" : filehash,
            "fileaddr" : fileaddr,
        }
        # send.send(f"{filename}{SEPARATOR}{filesize}{SEPARATOR}{filetype}{SEPARATOR}{filehash}{SEPARATOR}{fileaddr}".encode())
        send.sendall(pickle.dumps(info))
        filehash = ""
        with open(filename, "rb") as f:
            filehash = get_hash(filename, 15)
            print(filehash)
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                send.sendall(bytes_read)
        stx.add_output(filehash, host, filename)
        send.close()
        os.remove(filename)
        
    stx.gen_tx_hash()
    mem.add_transaction(stx)
    udp.broadcastmessage(json.dumps(stx.to_json()))

def get_hash(filename, parts):
    hash_ar = []
    file_size = os.stat(filename)
    block_size = math.ceil(file_size.st_size/parts)
    with open(filename,"rb") as file:
        chunk = file.read(block_size)
        while chunk:
            hash = hashlib.sha256()
            hash.update(chunk)
            hash_ar.append(hash.hexdigest())
            chunk = file.read(block_size)
    hsh = calculate_merkle_root(hash_ar)
    return hsh

def calculate_merkle_root(transactions=[]):
    new_tran = []
    if len(transactions) > 1:
        if transactions[-1] == transactions[-2]:
            return ""
    for i in range(0, len(transactions), 2):
        h = hashlib.sha256()
        if i+1 == len(transactions):
            h.update(
                ((transactions[i]) + (transactions[i])).encode("UTF-8"))
            new_tran.append(h.hexdigest())
        else:
            h.update(
                ((transactions[i]) + (transactions[i+1])).encode("UTF-8"))
            new_tran.append(h.hexdigest())

    if len(new_tran) == 1:
        return new_tran[0]
    else:
        return calculate_merkle_root(new_tran)