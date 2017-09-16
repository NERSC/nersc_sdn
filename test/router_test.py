#
# See LICENSE for full text.

import unittest
import router
from time import time, sleep
from pymongo import MongoClient
from initdb import init
from job_server import server
import os


class RouterTestCase(unittest.TestCase):

    def setUp(self):
        self.settings = {
            'DBHOST': 'localhost',
            'RTRUSER': 'sdn',
            'MAPFILE': 'test/mapfile',
            'JOBSURL': 'http://localhost:8000',
            'POLLINTERVAL': '0.1'
        }
        client = MongoClient("localhost")
        self.routes = client["sdn"].routes
        self.initdb()
        self.router = router.Router(self.settings)
        self.jobfile = '/tmp/sqjobs'
        self.data = {'user': 'auser',
                     'end_time': time()+60,
                     'jobid': '1234'}

    def tearDown(self):
        self.router.shutdown()
        if os.path.exists(self.jobfile):
            os.remove(self.jobfile)

    @classmethod
    def setUpClass(cls):
        cls.s = server()
        cls.sdfile = '/tmp/shutdown_sdn'
        if os.path.exists(cls.sdfile):
            os.remove(cls.sdfile)

    @classmethod
    def tearDownClass(cls):
        cls.s.terminate()
        # Trigger a shutdown with the magic file
        with open(cls.sdfile, 'w') as f:
            f.write('')
        # Give it time to trigger
        sleep(1)
        os.remove(cls.sdfile)

    def initdb(self):
        init('localhost', '1.2.3', 4, 4)

    def test_db(self):
        self.routes.remove()
        with self.assertRaises(OSError):
            router.Router(self.settings)

    def test_available(self):  # Test available call
        avail = self.router.available()
        self.assertIn('1.2.3.4', avail)

    def test_status(self):
        status = self.router.status()
        self.assertEquals(status[0]['status'], 'available')

    def test_associate(self):
        self.initdb()
        data = self.data
        address = self.router.associate({'ip': '10.128.0.1'}, data)
        self.assertEquals(address, '1.2.3.4')
        rec = self.routes.find_one({'ip': '10.128.0.1'})
        self.assertIsNotNone(rec)
        self.assertEquals(rec['user'], 'auser')

        address = self.router.associate({'ip': '10.128.0.1'}, data)
        self.assertEquals(address, '1.2.3.4')

        # This shoulf fail
        address = self.router.associate({'ip': '10.128.0.2'}, data)
        self.assertIsNone(address)

        self.initdb()
        with self.assertRaises(ValueError):
            address = self.router.associate({'ip': '10.128.1.2'}, data)

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

    def test_timer(self):
        rec = {
            'address': '1.2.3.4',
            'ip': '10.128.0.1',
            'router': 'router',
            'last_associated': time(),
            'end_time': time()+2,
            'user': 'auser',
            'jobid': '1234',
            'status': 'used'
        }
        rec2 = {
            'address': '1.2.3.5',
            'ip': '10.128.0.2',
            'router': 'router',
            'last_associated': time(),
            'end_time': time()+10000,
            'user': 'buser',
            'jobid': '1235',
            'status': 'used'
        }
        self.routes.remove()
        self.routes.insert(rec)
        self.routes.insert(rec2)
        sleep(1)
        rec = self.routes.find_one({'address': '1.2.3.4'})
        self.assertEquals(rec['status'], 'used')
        sleep(2)
        rec = self.routes.find_one({'address': '1.2.3.4'})
        self.assertEquals(rec['status'], 'available')
        # The second job should still be there
        rec = self.routes.find_one({'address': '1.2.3.5'})
        self.assertEquals(rec['status'], 'used')

    def test_jobid(self):
        # Test job id
        rec = {
            'address': '1.2.3.4',
            'ip': '10.128.0.1',
            'router': 'router',
            'last_associated': time(),
            'end_time': time()+10,
            'user': 'auser',
            'jobid': '1233',
            'status': 'used'
        }
        self.routes.remove({})
        self.routes.insert(rec)
        # Update mock file with job 1233 running
        with open(self.jobfile, 'w') as f:
            f.write('1233\n')
        sleep(2)
        # Should still be there
        rec = self.routes.find_one({'address': '1.2.3.4'})
        self.assertEquals(rec['status'], 'used')
        # Now let have the job go away and a new job is running
        with open(self.jobfile, 'w') as f:
            f.write('1234\n')
        sleep(2)
        rec = self.routes.find_one({'address': '1.2.3.4'})
        self.assertEquals(rec['status'], 'available')
