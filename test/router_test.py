#
# See LICENSE for full text.

import unittest
import router
from pymongo import MongoClient
from initdb import init


class RouterTestCase(unittest.TestCase):

    def setUp(self):
        self.settings = {
            'DBHOST': 'localhost',
            'RTRUSER': 'sdn',
            'MAPFILE': 'test/mapfile'
        }
        client = MongoClient("localhost")
        self.routes = client["sdn"].routes
        self.initdb()
        self.router = router.Router(self.settings)

    def initdb(self):
        init('localhost', '1.2.3', 4, 4)

    def test_db(self):
        self.routes.remove()
        with self.assertRaises(OSError):
            router.Router(self.settings)

    def test_available(self):
        avail = self.router.available()
        print avail
        self.assertIn('1.2.3.4', avail)

    def test_status(self):
        status = self.router.status()
        self.assertEquals(status[0]['status'], 'available')

    def test_associate(self):
        self.initdb()
        address = self.router.associate({'ip': '10.128.0.1'})
        self.assertEquals(address, '1.2.3.4')

        address = self.router.associate({'ip': '10.128.0.1'})
        self.assertEquals(address, '1.2.3.4')

        # This shoulf fail
        address = self.router.associate({'ip': '10.128.0.2'})
        self.assertIsNone(address)

        self.initdb()
        with self.assertRaises(ValueError):
            address = self.router.associate({'ip': '10.128.1.2'})

    def test_release(self):
        self.routes.remove({})
        rec = {
            'address': '1.2.3.4',
            'ip': '10.128.0.1',
            'router': 'router',
            'last_associated': '2017',
            'status': 'used'
        }
        self.routes.insert(rec)
        status = self.router.release('10.128.0.1')
        self.assertEquals(status, 'released')

        status = self.router.release('10.128.0.1')
        self.assertEquals(status, 'released')
