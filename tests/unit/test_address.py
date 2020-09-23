import unittest
from trucoin.Address import Address

class TestAddress(unittest.TestCase):

    def gen_words(self):
        add = Address()
        print(add.gen_words())

    def gen_addr(self):
        add = Address()
        print(add.get_public_address())

    def sign_verif(self):
        add = Address()
        sgn = add.sign_message("hello world")
        res = add.verify_signature("hello world", sgn)
        self.assertEqual(res, True)

if __name__ == '__main__':
    unittest.main()