from trucoin.Mempool import Mempool
from trucoin.Transaction import Transaction
from trucoin.TransactionInput import TransactionInput
from trucoin.TransactionOutput import TransactionOutput
import unittest

class TestMempool(unittest.TestCase):

    def test_add_transaction(self):
        tx = Transaction()
        input = TransactionInput()
        input.address = "test_address"
        tx.add_input(input)
        tx.generate_hash()

        mp = Mempool()
        mp.flush_mempool()
        mp.add_transaction(tx)

        self.assertEqual(mp.get_size(), 1)
        mp.close()

    def test_remove_transaction(self):
        tx = Transaction()
        input = TransactionInput()
        input.address = ""
        tx.add_input(input)
        tx.generate_hash()

        mp = Mempool()
        mp.flush_mempool()
        mp.add_transaction(tx)
        self.assertEqual(mp.get_size(), 1)
        mp.remove_transaction(tx.hash)
        self.assertEqual(mp.get_size(), 0)
        mp.close()

    def test_get_transaction(self):
        tx = Transaction()
        input = TransactionInput()
        input.address = ""
        tx.add_input(input)
        tx.generate_hash()

        mp = Mempool()
        mp.flush_mempool()
        mp.add_transaction(tx)
        self.assertEqual(mp.get_transaction().to_json(), tx.to_json())
        mp.close()


if __name__ == '__main__':
    unittest.main()
