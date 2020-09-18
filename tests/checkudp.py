
import socket
import json
host = '0.0.0.0'
port = 8000
sock= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((host, port))
message = {
    "hash": "588b31928713134419d1d12feca72b82e776db1595c6c364d9d44a641b366eda",
    "timestamp": 1599679655,
    "transactions": [
        {
            "timestamp": 1599679655.400641,
            "version": "0.0.1",
            "hash": "d7b8cdb24865cae0af0a297751e597bac45f37e08491dc0688bcc953c62dfcdc",
            "inputs": [
                {
                    "previous_tx": "16e8dab3a9185d5329fac9cfdc0a81c7817826f701e747cb3751878061e4dc8c",
                    "index": 0,
                    "scriptSig": [
                        "d6225d039d0c94dfda2efd8827c2bb867771bef312dcdc487e6ce7c8acbcf58da0eeed0b9dd381b70e888bda5dee428f"
                    ],
                    "verifying_key": [
                        "-----BEGIN PUBLIC KEY-----\nMEkwEwYHKoZIzj0CAQYIKoZIzj0DAQEDMgAEHxzkpgh/lqgd1/rb7d+D+srhlhzG\ncOAveBQafVnHkffNR2aCiFHVQZKzhyO7iC/p\n-----END PUBLIC KEY-----\n"
                    ],
                    "address": "1d3f347aada53547142da8edea5e0019e6ef31bb15"
                },
                {
                    "previous_tx": "16e8dab3a9185d5329fac9cfdc0a81c7817826f701e747cb3751878061e4dc8c",
                    "index": 0,
                    "scriptSig": [
                        "59692739010300730ca09f6f88db68ce22d41a2c38018b6d7233b66d56a9816e2335459175c676f8d451063da079570c"
                    ],
                    "verifying_key": [
                        "-----BEGIN PUBLIC KEY-----\nMEkwEwYHKoZIzj0CAQYIKoZIzj0DAQEDMgAEHxzkpgh/lqgd1/rb7d+D+srhlhzG\ncOAveBQafVnHkffNR2aCiFHVQZKzhyO7iC/p\n-----END PUBLIC KEY-----\n"
                    ],
                    "address": "1d3f347aada53547142da8edea5e0019e6ef31bb15"
                },
                {
                    "previous_tx": "16e8dab3a9185d5329fac9cfdc0a81c7817826f701e747cb3751878061e4dc8c",
                    "index": 0,
                    "scriptSig": [
                        "2f6483c3a87317759b7a9687922771ba433c3dd3dc6d39bec3660023b9f53f60a77fe38632ef1cd3cfac001e72b069af"
                    ],
                    "verifying_key": [
                        "-----BEGIN PUBLIC KEY-----\nMEkwEwYHKoZIzj0CAQYIKoZIzj0DAQEDMgAEHxzkpgh/lqgd1/rb7d+D+srhlhzG\ncOAveBQafVnHkffNR2aCiFHVQZKzhyO7iC/p\n-----END PUBLIC KEY-----\n"
                    ],
                    "address": "1d3f347aada53547142da8edea5e0019e6ef31bb15"
                },
                {
                    "previous_tx": "16e8dab3a9185d5329fac9cfdc0a81c7817826f701e747cb3751878061e4dc8c",
                    "index": 0,
                    "scriptSig": [
                        "9b5aa96b16cacc7f09d0392bbc16f0946dbf4982f6a17284f8475b75035256eef7a960553fc1af3ce3384c4e0a3eb824"
                    ],
                    "verifying_key": [
                        "-----BEGIN PUBLIC KEY-----\nMEkwEwYHKoZIzj0CAQYIKoZIzj0DAQEDMgAEHxzkpgh/lqgd1/rb7d+D+srhlhzG\ncOAveBQafVnHkffNR2aCiFHVQZKzhyO7iC/p\n-----END PUBLIC KEY-----\n"
                    ],
                    "address": "1d3f347aada53547142da8edea5e0019e6ef31bb15"
                },
                {
                    "previous_tx": "16e8dab3a9185d5329fac9cfdc0a81c7817826f701e747cb3751878061e4dc8c",
                    "index": 0,
                    "scriptSig": [
                        "d61110719d64305dc43d2dbf2da111a055d636a8b73444dee268f50b9ed40bff2ece1785ed4ee4685f78056f49412eb6"
                    ],
                    "verifying_key": [
                        "-----BEGIN PUBLIC KEY-----\nMEkwEwYHKoZIzj0CAQYIKoZIzj0DAQEDMgAEHxzkpgh/lqgd1/rb7d+D+srhlhzG\ncOAveBQafVnHkffNR2aCiFHVQZKzhyO7iC/p\n-----END PUBLIC KEY-----\n"
                    ],
                    "address": "1d3f347aada53547142da8edea5e0019e6ef31bb15"
                }
            ],
            "outputs": [
                {
                    "value": 25,
                    "n": 0,
                    "address": "yikgyyf67rr68t887tfc"
                },
                {
                    "value": 25,
                    "n": 0,
                    "address": "yikgyyf67rr68t887tfc"
                },
                {
                    "value": 25,
                    "n": 0,
                    "address": "yikgyyf67rr68t887tfc"
                },
                {
                    "value": 25,
                    "n": 0,
                    "address": "yikgyyf67rr68t887tfc"
                },
                {
                    "value": 25,
                    "n": 0,
                    "address": "yikgyyf67rr68t887tfc"
                }
            ],
            "block": "Mempool"
        }
    ],
    "previous_block_hash": "6ecf0a86d82851a63147fa8cc4f95b4bb73a39a341493da66a03198fed7fd939",
    "merkle_root": "8c60a09d3824081875de7e3f3010b0327769f2603e07c28c901f23557bb2479b",
    "height": 5,
    "version": "0.0.1",
    "size": 573
}
sock.sendto(json.dumps(message).encode('utf-8'),("127.0.0.1",6500))