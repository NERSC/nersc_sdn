#!/usr/bin/python

import pexpect


class vyosInterface:
    def __init__(self):
        self.user = "canon"
        self.prompt = self.user+"@.*$"
        print "Initializing VYOS Interface"

    def nid_to_int_address(self, nid):
        third = nid/254
        fourth = nid%254
        if third>0:
          fourth += 1
        return "10.128.%d.%d" % ( third, fourth)

    def get_rule(self, address):
        last = int(address.split('.')[3])
        return last+40

    def add_nat(self, nid, router, address):
        # Mock stubs
        # do update
        rule = self.get_rule(address)
        int_add = self.nid_to_int_address(nid)
        interface = "bond1"
        vif = 224
        print "Adding NAT"
        print "nid=%d router=%s address=%s rule=%d int_add=%s" % (nid, router, address, rule, int_add)
 
        child = pexpect.spawn('ssh %s@%s' % (self.user, router))
        child.expect(self.prompt)
        print "Got prompt"
        child.sendline("configure")
        child.expect(self.prompt)
        child.sendline("set interfaces bonding %s vif %d address '%s/24'" % (interface, vif, address))
        child.expect(self.prompt)
        child.sendline("commit")
        child.expect(self.prompt)
        child.sendline("set nat destination rule %d description '1-to-1 NAT example'" % (rule))
        child.expect(self.prompt)
        child.sendline("set nat destination rule %d destination address '%s'" % (rule, address))
        child.expect(self.prompt)
        child.sendline("set nat destination rule %d inbound-interface '%s.%d'" % (rule, interface, vif))
        child.expect(self.prompt)
        print child.before
        child.sendline("set nat destination rule %d translation address '%s'" % (rule, int_add))
        child.expect(self.prompt)
        child.sendline("set nat source rule %d description '1-to-1 NAT example'" % (rule))
        child.expect(self.prompt)
        child.sendline("set nat source rule %d outbound-interface '%s.%d'" % (rule, interface, vif))
        child.expect(self.prompt)
        child.sendline("set nat source rule %d source address '%s'" % (rule, int_add))
        child.expect(self.prompt)
        child.sendline("set nat source rule %d translation address '%s'" % (rule, address))
        child.expect(self.prompt)
        child.sendline("commit add nat")
        child.expect(self.prompt)
        print child.before
        child.sendline("exit")
        child.expect(self.prompt)
        child.sendline("exit")
        print child.before
        return True

    def remove_nat(self, nid, router, address):
        # Mock stubs
        rule = self.get_rule(address)
        interface = "bond1"
        vif = 224
        print "Remove NAT"
        print "nid=%d router=%s address=%s rule=%d" % (nid, router, address, rule)
        child = pexpect.spawn('ssh %s@%s' % (self.user, router))
        child.expect(self.prompt)
        child.sendline("configure")
        child.expect(self.prompt)
        child.sendline("delete interfaces bonding %s vif %d address '%s/24'" % (interface, vif, address))
        child.expect(self.prompt)
        child.sendline("delete nat destination rule %d" % (rule))
        child.expect(self.prompt)
        child.sendline("delete nat source rule %d" % (rule))
        child.expect(self.prompt)
        child.sendline("commit remove nat")
        child.expect(self.prompt)
        print child.before
        child.sendline("exit")
        print child.before
        child.sendline("exit")
        return True
