#!/usr/bin/python

import pexpect


class vyosInterface:
    def __init__(self):
        self.user = "canon"
        self.prompt = self.user+"@.*:"
        print "Initializing VYOS Interface"

    def add_nat(self, nid, router, address):
        # Mock stubs
        # do update
        print "Adding NAT"
        print "nid=%d router=%s address=%s" % (nid, router, address)
        child = pexpect.spawn('ssh %s@%s' % (self.user, router))
        child.expect(self.prompt)
        child.sendline('echo %d %s' % (nid, address))
        child.expect(self.prompt)
        print child.before
        return True

    def remove_nat(self, nid, router, address):
        # Mock stubs
        print "Adding NAT"
        print "nid=%d router=%s address=%s" % (nid, router, address)
        child = pexpect.spawn('ssh %s@%s' % (self.user, router))
        child.expect(self.prompt)
        child.sendline('echo release %d %s' % (nid, address))
        child.expect(self.prompt)
        print child.before
        return True
