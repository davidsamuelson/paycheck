import unittest
from random import randint
from paycheck import with_checker, register_type


# some fancy new types

def generate_mac_addr():
    '''
    Returns a mac address in the form
    XX:XX:XX:XX:XX:XX, where each X is a
    lowercase hexadecimal digit.
    '''
    return ':'.join([hex(randint(0, 255))[2:] for x in range(6)])

register_type('mac', generate_mac_addr)


class TestRegisterType(unittest.TestCase):

    @with_checker('mac')
    def test_mac(self, mac):
        self.assertTrue(len(mac.split(':')) == 6)

    
tests = [TestRegisterType]

if __name__ == '__main__':
    unittest.main()
