#
# See LICENSE for full text.

import unittest
import os

from nersc_sdn.ddns import DDNS


class DDNSTestCase(unittest.TestCase):

    def setUp(self):
        self.ddns = DDNS(base='services.my.org',
                         keyfile='./kf',
                         server='ns.my.org',
                         zone='my.org')
        self.hf = './hostfile'

    def tearDown(self):
        pass

    def test_add(self):
        if os.path.exists(self.hf):
            os.remove(self.hf)
        self.ddns.add_dns('1234', '1.2.3.4')
        with open(self.hf) as f:
            line = f.read().rstrip()
        name = 'job1234.services.my.org.'
        self.assertEquals(line, '1.2.3.4 ' + name)

    def test_del(self):
        if os.path.exists(self.hf):
            os.remove(self.hf)
        name = 'job1234.services.my.org.'
        with open(self.hf, 'w') as f:
            f.write('1.2.3.4 %s\n' % (name))
        self.ddns.del_dns('1234')
        with open(self.hf) as f:
            line = f.read().rstrip()
        self.assertEquals(line, '')

    def test_init(self):
        with self.assertRaises(ValueError):
            self.ddns = DDNS(keyfile='./kf',
                             server='ns.my.org',
                             zone='my.org')
        with self.assertRaises(ValueError):
            self.ddns = DDNS(base='base',
                             server='ns.my.org')
        d = self.ddns = DDNS(base='base',
                             zone='my.org')
        self.assertEquals('ns.base', d.server)
