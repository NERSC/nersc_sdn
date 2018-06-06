#
# See LICENSE for full text.

import unittest
import os
import json
from time import time
from pymongo import MongoClient
from sdninitdb import init


class APITestCase(unittest.TestCase):

    def setUp(self):
        client = MongoClient("localhost")
        self.routes = client["sdn"].routes
        self.initdb()
        td = os.path.dirname(os.path.realpath(__file__))
        os.environ['SDN_SETTINGS'] = "%s/settings.ini" % (td)
        from nersc_sdn import sdnapi
        astr = "good:root:root::0:0:nid0001:10.128.0.1"
        self.allowed = {'authentication': astr}

        astr = "bad:root:root::0:0:nid0001:10.128.0.1"
        self.badauth = {'authentication': astr}

        astr = "good:user:user::500:500:nid0001:10.128.0.1"
        self.unallowed = {'authentication': astr}

        astr = "good:root:root::0:0:nid0001:10.128.1.1"
        self.bogusip = {'authentication': astr}

        self.app = sdnapi.application.test_client()
        self.sdnapi = sdnapi

        self.data = {'uid': 501, 'user': 'auser',
                     'end_time': time()+60,
                     'jobid': '1234'
                     }

    def tearDown(self):
        self.sdfile = '/tmp/shutdown_sdn'
        self.sdnapi.shutdown()

    def initdb(self):
        init('localhost', '1.2.3', 4, 4)

    def test_testauth(self):
        from nersc_sdn.sdnapi import is_allowed
        status = is_allowed({})
        self.assertEquals(status, False)

    def test_hello(self):
        rv = self.app.get('/')
        self.assertEquals(rv.status_code, 200)

    def test_ping(self):
        rv = self.app.get('/_ping')
        self.assertEquals(rv.status_code, 200)

    def test_addresses(self):
        """
        Test address call
        """
        rv = self.app.get('/v1/addresses/', headers=self.allowed)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/v1/addresses/', headers=self.badauth)
        self.assertEquals(rv.status_code, 404)

        rv = self.app.get('/v1/addresses/', headers=self.unallowed)
        self.assertEquals(rv.status_code, 401)

    def test_status(self):
        """
        Test status call
        """

        rv = self.app.get('/v1/status/', headers=self.allowed)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/v1/status/', headers=self.badauth)
        self.assertEquals(rv.status_code, 404)

        rv = self.app.get('/v1/status/', headers=self.unallowed)
        self.assertEquals(rv.status_code, 401)

    def test_associate(self):
        """
        Test various associate  modes
        """
        self.initdb()
        d = json.dumps(self.data)
        good = self.allowed
        bad = self.badauth
        unallowed = self.unallowed
        rv = self.app.post('/v1/associate/', headers=good, data=d)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.post('/v1/associate/', headers=self.bogusip, data=d)
        self.assertEquals(rv.status_code, 404)

        rv = self.app.post('/v1/associate/10.128.0.1', headers=good, data=d)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.post('/v1/associate/10.128.1.1', data=d)
        self.assertEquals(rv.status_code, 404)

        rv = self.app.post('/v1/associate/10.128.0.1', headers=good)
        self.assertEquals(rv.status_code, 404)

        self.initdb()
        rv = self.app.post('/v1/associate/10.128.0.1', headers=bad, data=d)
        self.assertEquals(rv.status_code, 404)

        rv = self.app.post('/v1/associate/', headers=unallowed, data=d)
        self.assertEquals(rv.status_code, 401)

        rv = self.app.post('/v1/associate/10.128.0.1', headers=unallowed,
                           data=d)
        self.assertEquals(rv.status_code, 401)

    def test_release(self):
        self.routes.remove({})
        rec = {
            'address': '1.2.3.4',
            'ip': '10.128.0.1',
            'router': 'router',
            'last_associated': '2017',
            'status': 'used',
            'jobid': '1234'
        }
        self.routes.insert(rec)
        rv = self.app.get('/v1/release/', headers=self.allowed)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/v1/release/10.128.0.1', headers=self.allowed)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/v1/release/', headers=self.bogusip)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/v1/release/10.128.0.1', headers=self.bogusip)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/v1/release/', headers=self.unallowed)
        self.assertEquals(rv.status_code, 401)

        rv = self.app.get('/v1/release/10.128.0.1', headers=self.unallowed)
        self.assertEquals(rv.status_code, 401)


if __name__ == '__main__':
    unittest.main()
