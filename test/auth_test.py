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

import os
import unittest
from nersc_sdn import auth
from nersc_sdn import munge


class MungeTestCase(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__)) + \
                        "/../test/"
        self.encoded = "xxxx\n"
        self.message = "test"
        self.expired = "expired"
        with open(self.test_dir + "tbin/.munge.test", 'w') as f:
            f.write(self.encoded)

    def tearDown(self):
        with open(self.test_dir + "tbin/.munge.expired", 'w') as f:
            f.write('')

    def test_noauth(self):
        with self.assertRaises(KeyError):
            auth.Authentication({})

        with self.assertRaises(NotImplementedError):
            auth.Authentication({'authentication': 'bogus'})

    def test_munge(self):
        resp = munge.munge(self.message, socket="/fake.socket")
        self.assertIsNotNone(resp)

        authh = auth.Authentication({'authentication': 'munge'})
        resp = authh.authenticate(self.encoded)
        self.assertIsNotNone(resp)

        with self.assertRaises(KeyError):
            resp = authh.authenticate(None)

    def test_mock(self):
        authh = auth.Authentication({'authentication': 'mock'})
        with self.assertRaises(OSError):
            authh.authenticate('')
