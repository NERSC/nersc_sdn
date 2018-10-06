#
# See LICENSE for full text.

import unittest
from nersc_sdn import router
from time import time, sleep
from pymongo import MongoClient
from sdninitdb import init
from job_server import server
import os
from multiprocessing.process import Process


class RouterTestCase(unittest.TestCase):

    def setUp(self):
        self.settings = {
            'DBHOST': 'localhost',
            'RTRUSER': 'sdn',
            'RTRKEY': 'keyfile',
            'MAPFILE': 'test/mapfile',
            'JOBSURL': 'http://localhost:8000',
            'POLLINTERVAL': '0.1',
            'DNS_BASE': 'jobs.domain.org',
            'DNS_PREFIX': 'job',
            'DNS_ZONE': 'domain.org',
            'DNS_SERVER': 'ns.domain.org',
            'DNS_KEYFILE': './kf'
        }
        client = MongoClient("localhost")
        self.db = client["sdn"]
        self.routes = self.db.routes
        self.initdb()
        self.router = router.Router(self.settings)
        self.jobfile = '/tmp/sqjobs'
        self.data = {'user': 'auser',
                     'uid': 501,
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
            'uid': 501,
            'user': 'auser',
            'jobid': '1234',
            'status': 'used'
        }
        self.routes.insert(rec)
        status = self.router.release('10.128.0.1')
        self.assertEquals(status, 'released')

        status = self.router.release('10.128.0.1')
        self.assertEquals(status, 'released')
        nrec = self.routes.find_one({'address': '1.2.3.4'})
        self.assertIsNone(nrec['user'])
        self.assertIsNone(nrec['jobid'])
        self.assertIsNone(nrec['router'])
        self.assertEquals(nrec['status'], 'available')

    def test_timer(self):
        rec = {
            'address': '1.2.3.4',
            'ip': '10.128.0.1',
            'router': 'router',
            'last_associated': time(),
            'end_time': time()+2,
            'uid': 501,
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
            'uid': 502,
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
            'uid': 501,
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

    def test_slurm(self):
        jobs = self.router._get_slurm()
        self.assertIn('1234', jobs)

    def test_get_jobs(self):
        jobs = self.router.get_jobs()
        self.assertIn('1234', jobs)
        back = self.router.agent
        self.router.agent = 'local'
        jobs = self.router.get_jobs()
        self.assertIn('1234', jobs)
        self.router.agent = back

    def test_check_jobs(self):
        rec = {
            'address': '1.2.3.4',
            'ip': '10.128.0.1',
            'router': 'router',
            'last_associated': time(),
            'end_time': time()+10,
            'uid': 501,
            'user': 'auser',
            'jobid': '1233',
            'status': 'used'
        }
        rec2 = rec.copy()
        rec2['address'] = '1.2.3.5'
        rec2['ip'] = '10.128.0.2'
        rec2['jobid'] = '1234'
        rec3 = rec.copy()
        rec3['address'] = '1.2.3.6'
        rec3['ip'] = '10.128.0.2'
        del rec3['jobid']
        self.routes.insert(rec)
        self.routes.insert(rec2)
        self.routes.insert(rec3)
        self.router.check_jobs(['1234'])
        # Job 1234 should still be there
        r = self.routes.find_one({'jobid': '1234'})
        self.assertIsNotNone(r)
        # Job 1233 should be gone
        r = self.routes.find_one({'jobid': '1233'})
        self.assertIsNone(r)
        # rec3 should still be there
        r = self.routes.find_one({'address': '1.2.3.6'})
        self.assertIsNotNone(r)

    def _shutdown(self):
        sd2 = "/tmp/shut2"
        sleep(0.3)
        with open(sd2, "w") as f:
            f.write("blah")

    def test_cleanup(self):
        """
        Test the cleanup thread
        """
        # We want the cleanup thread to run in this context
        # but it is an infitite loop.  So let's delay a shtudown.
        sd2 = "/tmp/shut2"
        rec = {
            'address': '1.2.3.4',
            'ip': '10.128.0.1',
            'router': 'router',
            'last_associated': time(),
            'end_time': 0,
            'uid': 501,
            'user': 'auser',
            'jobid': '1233',
            'status': 'used'
        }
        self.db.routes2.insert(rec)
        # We want to shutdown the thread that is started on init
        with open(sd2, 'w') as f:
            f.write('1')
        settings = self.settings.copy()
        settings['COLLECTION'] = 'routes2'
        settings['SHUTFILE'] = sd2
        rt = router.Router(settings)
        # Wait for the init thread to shutdown
        sleep(0.2)
        # Now let's start our own
        if os.path.exists(sd2):
            os.remove(sd2)
        shut = Process(target=self._shutdown)
        shut.start()
        rt.cleanup()
        shut.terminate()
        r = self.db.routes2.find_one({'address': '1.2.3.4'})
        self.assertEquals(r['status'], 'available')
        self.db.routes2.remove({})
        rv = rt.cleanup()
        self.assertEquals(-1, rv)

    def test_notinitalized(self):
        settings = self.settings.copy()
        settings['COLLECTION'] = 'routes3'
        with self.assertRaises(OSError):
            router.Router(settings)

    def test_initdns(self):
        """
        Test init DNS
        """
        set = {
            'DNS_BASE': 'base',
            'DNS_ZONE': 'zone',
            'DNS_SERVER': 'server',
            'DNS_KEYFILE': 'keyfile'
        }
        with self.assertRaises(ValueError):
            self.router._init_dns(set)
        self.assertIsNone(self.router._init_dns({}))
