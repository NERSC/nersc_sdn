# Shifter, Copyright (c) 2015, The Regents of the University of California,
# through Lawrence Berkeley National Laboratory (subject to receipt of any
# required approvals from the U.S. Dept. of Energy).  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#  3. Neither the name of the University of California, Lawrence Berkeley
#     National Laboratory, U.S. Dept. of Energy nor the names of its
#     contributors may be used to endorse or promote products derived from this
#     software without specific prior written permission.`
#
# See LICENSE for full text.

import unittest
import requests
import job_server
import SocketServer


class ServerTestCase(unittest.TestCase):

    def setUp(self):
        self.handler = SocketServer.BaseRequestHandler(None, None, None)
        self.handler.__class__ = job_server.S
        pass

    def tearDown(self):
        pass

    def test_server(self):
        s = job_server.server()
        r = requests.get('http://localhost:8000')
        self.assertEquals(r.status_code, 200)
        s.terminate()

    def test_get(self):
        self.handler.request_version = 'HTTP/1.0'
        with open('/tmp/tfile', 'w') as f:
            self.handler.wfile = f
            self.handler.do_GET()
        with open('/tmp/tfile') as f:
            out = f.read()
        self.assertTrue(out.find('1234'))
