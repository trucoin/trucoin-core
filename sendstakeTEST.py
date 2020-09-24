import requests
import json
import time
from trucoin.Node import Node

if __name__ == '__main__':
    no = Node()
    myno = no.load_node_json()
    addr = myno["address"]
    tx = {
        'timestamp': time.time(),
        'version': '0.0.2',
        'inputs': [
            {
                "previous_tx": "oihrsgiohsioj9ih05i0yu9u59y8o4yu54h",
                "index": 3,
                "address": addr,
                "scriptSig": ["segbikldrih95euy9u4509uyh90e9p4ujy"],
                "verifying_key": ["jlbuigfuiga89y89egyg8w4oig8gw"]
            }
        ],
        'outputs': [
            {
                'value': 5,
                'n': 0,
                'address': '12345'
            }
        ],
        'hash': 'eef9fda50a6bf6c11c5078d8772d94df4f60ce54573c009f145eb047426ad0fb',
        'block': 'testchain',
        'is_coinbase': False
    }

    url = "http://34.75.37.203:8000/"
    headers = {
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTk4Mjk4ODIyLCJqdGkiOiJkNDQ1MDZkNmJjOGY0NjQxYWJlNmQyMzI2NzI5OTI5MCIsInVzZXJfaWQiOjF9.zk3CUn8XXvhZE0WsARUzr2IogPfB3XPzAp68zgJ7Kus',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps({
        'command': 'addtransaction',
        'body': tx
    }))
