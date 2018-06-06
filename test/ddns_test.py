#
# See LICENSE for full text.

import unittest

from nersc_sdn.ddns import DDNS


class DDNSTestCase(unittest.TestCase):

    def setUp(self):
        self.ddns = DDNS(base='services.my.org',
                         keyfile='./kf',
                         server='ns.my.org',
                         zone='my.org')
        pass

    def tearDown(self):
        pass

    def test_add(self):
        self.ddns.add_dns('test', '1.2.3.4')

    def test_del(self):
        self.ddns.del_dns('test')
