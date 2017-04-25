#!/usr/bin/python

import pexpect
import os


class vyosInterface:
    def __init__(self, user):
        print "Initializing VYOS Interface"
        self.user = user
        self.prompt = self.user+"@.*$"
        self.interface = "bond1"
        self.vif = 224

    def _get_rule(self, address):
        last = int(address.split('.')[3])
        return last+40

    def _sendline(self, child, line):
        child.sendline(line)
        child.expect(self.prompt)

    def add_nat(self, int_add, router, address):
        # Mock stubs
        # do update
        if 'MOCK' in os.environ:
            return True
        rule = self._get_rule(address)
        interface = self.interface
        vif = self.vif
        print "Adding NAT"
        print "router=%s address=%s rule=%d int_add=%s" % \
            (router, address, rule, int_add)
        p = pexpect.spawn('ssh %s@%s' % (self.user, router))
        p.expect(self.prompt)
        self._sendline(p, "configure")
        # Add interface
        self._sendline(p, "set interfaces bonding %s vif %d address '%s/24'"
                       % (interface, vif, address))
        self._sendline(p, "commit")
        # Add destination route
        prefix = "set nat destination rule %d" % (rule)
        desc = "1-to-1 NAT for %s to %s" % (int_add, address)
        self._sendline(p, "%s description '%s'" % (prefix, desc))
        self._sendline(p, "%s destination address '%s'" % (prefix, address))
        self._sendline(p, "%s inbound-interface '%s.%d'" %
                       (prefix, interface, vif))
        self._sendline(p, "%s translation address '%s'" % (prefix, int_add))
        # Add source route
        prefix = "set nat source rule %d" % (rule)
        self._sendline(p, "%s description '%s'" % (prefix, desc))
        self._sendline(p, "%s outbound-interface '%s.%d'" %
                       (prefix, interface, vif))
        self._sendline(p, "%s source address '%s'" % (prefix, int_add))
        self._sendline(p, "%s translation address '%s'" % (prefix, address))
        self._sendline(p, "commit add nat")
        self._sendline(p, "exit")
        p.sendline("exit")
        return True

    def remove_nat(self, router, address):
        # Mock stubs
        if 'MOCK' in os.environ:
            return True

        rule = self._get_rule(address)
        interface = "bond1"
        vif = self.vif
        print "Remove NAT"
        print "router=%s address=%s rule=%d" % (router, address, rule)
        p = pexpect.spawn('ssh %s@%s' % (self.user, router))
        p.expect(self.prompt)
        self._sendline(p, "configure")
        self._sendline(p, "delete interfaces bonding %s vif %d address '%s/24'"
                       % (interface, vif, address))
        self._sendline(p, "delete nat destination rule %d" % (rule))
        self._sendline(p, "delete nat source rule %d" % (rule))
        self._sendline(p, "commit remove nat")
        self._sendline(p, "exit")
        p.sendline("exit")
        return True
