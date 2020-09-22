from trucoin.Mempool import Mempool
from trucoin.Block import Block
from trucoin.BlockChain import BlockChain


class Mining:
    def create_block(self):
        block = Block()
        block.create_coinbase_transaction()
        mempool = Mempool()
        blkc = BlockChain()

        mempool_size = mempool.get_len()
        if mempool_size == 0:
            return
        while mempool_size > 0:
            tx = mempool.get_transaction()
            block.add_transaction(tx)
            mempool_size -= 1
        
        block.calcalute_block_size()
        block.calculate_merkle_root()
        block.compute_hash()
        blkc.add_block(block)

        return block