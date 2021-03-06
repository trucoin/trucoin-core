import unittest
from trucoin.Transaction import Transaction
from trucoin.Block import Block
from trucoin.TransactionInput import TransactionInput

class TestBlock(unittest.TestCase):

    def test_merkle_root(self):
        block = Block()
        tx = Transaction()
        input = TransactionInput()
        input.address = "test_address"
        tx.add_input(input)
        tx.generate_hash()
        block.add_transaction(tx)
        block.calculate_merkle_root()
        initial_merkle_root = block.merkle_root

        tx1 = Transaction()
        input1 = TransactionInput()
        input1.address = "another_test_address"
        tx1.add_input(input1)
        tx1.generate_hash()
        block.add_transaction(tx1)
        block.calculate_merkle_root()
        final_merkle_root = block.merkle_root

        self.assertNotEqual(initial_merkle_root, final_merkle_root)

    # complete block test in addblock.py

if __name__ == '__main__':
    unittest.main()