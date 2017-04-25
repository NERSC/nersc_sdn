#
# See LICENSE for full text.

import unittest
import os
from pymongo import MongoClient
from initdb import init


class APITestCase(unittest.TestCase):

    def setUp(self):
        client = MongoClient("localhost")
        self.routes = client["sdn"].routes
        self.initdb()
        os.environ['SDN_SETTINGS'] = "./test/settings.ini"
        import sdnapi
        astr = "good:root:root::0:0:nid0001:10.128.0.1"
        self.allowed = {'authentication': astr}

        astr = "bad:root:root::0:0:nid0001:10.128.0.1"
        self.badauth = {'authentication': astr}

        astr = "good:user:user::500:500:nid0001:10.128.0.1"
        self.unallowed = {'authentication': astr}

        astr = "good:root:root::0:0:nid0001:10.128.1.1"
        self.bogusip = {'authentication': astr}

        self.app = sdnapi.application.test_client()

    def initdb(self):
        init('localhost', '1.2.3', 4, 4)

    def test_testauth(self):
        from sdnapi import is_allowed
        status = is_allowed({})
        self.assertEquals(status, False)

    def test_hello(self):
        rv = self.app.get('/')
        self.assertEquals(rv.status_code, 200)

    def test_ping(self):
        rv = self.app.get('/_ping')
        self.assertEquals(rv.status_code, 200)

    def test_addresses(self):
        rv = self.app.get('/addresses/', headers=self.allowed)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/addresses/', headers=self.badauth)
        self.assertEquals(rv.status_code, 404)

        rv = self.app.get('/addresses/', headers=self.unallowed)
        self.assertEquals(rv.status_code, 401)

    def test_status(self):
        rv = self.app.get('/status/', headers=self.allowed)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/status/', headers=self.badauth)
        self.assertEquals(rv.status_code, 404)

        rv = self.app.get('/status/', headers=self.unallowed)
        self.assertEquals(rv.status_code, 401)

    def test_associate(self):
        self.initdb()
        rv = self.app.get('/associate/', headers=self.allowed)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/associate/', headers=self.bogusip)
        self.assertEquals(rv.status_code, 404)

        rv = self.app.get('/associate/10.128.0.1', headers=self.allowed)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/associate/10.128.1.1')
        self.assertEquals(rv.status_code, 404)

        self.initdb()
        rv = self.app.get('/associate/10.128.0.1', headers=self.badauth)
        self.assertEquals(rv.status_code, 404)

        rv = self.app.get('/associate/', headers=self.unallowed)
        self.assertEquals(rv.status_code, 401)

        rv = self.app.get('/associate/10.128.0.1', headers=self.unallowed)
        self.assertEquals(rv.status_code, 401)

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
        rv = self.app.get('/release/', headers=self.allowed)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/release/10.128.0.1', headers=self.allowed)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/release/', headers=self.bogusip)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/release/10.128.0.1', headers=self.bogusip)
        self.assertEquals(rv.status_code, 200)

        rv = self.app.get('/release/', headers=self.unallowed)
        self.assertEquals(rv.status_code, 401)

        rv = self.app.get('/release/10.128.0.1', headers=self.unallowed)
        self.assertEquals(rv.status_code, 401)


if __name__ == '__main__':
    unittest.main()
