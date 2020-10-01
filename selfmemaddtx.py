import json
import time
from trucoin.Mempool import Mempool
from trucoin.Transaction import Transaction

if __name__ == '__main__':
    tx = {
        'timestamp': time.time(),
        'version': '0.0.2',
        'inputs': [
            {
                "previous_tx": "oihrsgiohsioj9ih05i0yu9u59y8o4yu54h",
                "index": 3,
                "address": "iuyfvuyfguyifguyff687",
                "scriptSig": ["segbikldrih95euy9u4509uyh90e9p4ujy"],
                "verifying_key": ["jlbuigfuiga89y89egyg8w4oig8gw"]
            }
        ],
        'outputs': [
            {
                'value': 50,
                'n': 0,
                'address': 'bb4c10de221933bb0aa1ab1897f5640592fc1fa4'
            }
        ],
        'hash': 'eef9fda50a6besdrhyaeeeeeeeeee5072d94df4f6sfrhdztrhewrhyf145eb047426ad0fb',
        'block': 'testchain',
        'is_coinbase': False
    }
    mm = Mempool()
    t = Transaction()
    ob = t.from_json(tx)
    print("Adding tx to own mempool only!!")
    mm.add_transaction(ob)
