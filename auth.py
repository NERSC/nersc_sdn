#!/usr/bin/env python
# NERSC SDN, Copyright (c) 2017, The Regents of the University of California,
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

"""
Lifted from Shifter (https://github.com/nersc/shifter)
Module to abstract authentication.  Currently just wraps munge.
"""

import munge


class Authentication(object):
    """
    Authentication Class to authenticate user requests
    """

    def __init__(self, config):
        """
        Initializes authenication handle.
        config is a dictionary.  It must define 'Authentication' and it must
        be a supported type (currently munge).
        Different auth mechanisms may require additional key value pairs
        """
        if 'authentication' not in config:
            raise KeyError('Authentication not specified')
        self.socket = None
        if config['authentication'] == "munge":
            if 'socket' in config:
                self.socket = config['socket']
            self.type = 'munge'
        elif config['authentication'] == "mock":
            self.type = 'mock'
        else:
            memo = 'Unsupported auth type %s' % (config['authentication'])
            raise NotImplementedError(memo)

    def _psplit(self, textstr):
        (v1, v2) = textstr.replace(' ', '').rstrip(')').split('(')
        return [v1, v2]

    def _authenticate_munge(self, authstr):

        if authstr is None:
            raise KeyError("No Auth String Provided")
        response = munge.unmunge(authstr, socket=self.socket)
        if response is None:
            raise OSError('Authentication Failed')
        ret = dict()
        (user, uid) = self._psplit(response['UID'])
        (group, gid) = self._psplit(response['GID'])
        (host, ip) = self._psplit(response['ENCODE_HOST'])

        ret = {
            'user': user, 'uid': int(uid),
            'group': group, 'gid': int(gid),
            'host': host, 'ip': ip,
            'message': response['MESSAGE']
        }

        return ret

    def _authenticate_mock(self, authstr):

        ret = dict()
        if authstr is None:
            raise KeyError("No Auth String Provided")
        auth = authstr.split(':')
        if len(auth) == 8:
            (status, user, group, token, uid, gid, host, ip) = auth
            ret = {'user': user, 'group': group, 'tokens': token,
                   'uid': int(uid), 'gid': int(gid),
                   'host': host, 'ip': ip}
        else:
            raise OSError('Bad AuthString')

        if status != 'good':
            raise OSError('Auth Failed st=%s' % status)

        return ret

    def authenticate(self, authstr):
        """
        authenticate a message
        authstr is the message to be validated.
        """
        if self.type == 'munge':
            return self._authenticate_munge(authstr)
        elif self.type == 'mock':
            return self._authenticate_mock(authstr)
        else:
            raise OSError('Unsupported auth type')
