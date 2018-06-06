from __future__ import print_function
from subprocess import Popen, PIPE


class DDNS:
    def __init__(self, keyfile='keyfile', base=None, server=None, zone=None,
                 prefix='job', lifetime=600):
        self.keyfile = keyfile
        if base is None:
            raise ValueError("Missing base")
        self.base = base
        if zone is None:
            raise ValueError("Missing zone")
        self.zone = zone
        if server is None:
            self.server = 'ns.' + self.base
        else:
            self.server = server
        self.ltime = lifetime
        self.prefix = prefix

    def _run_command(self, command, input):
        proc = Popen(command, stdout=PIPE, stdin=PIPE)
        proc.stdin.write(input)
        proc.stdin.close()
        proc.stdout.read()
        return proc.wait()

    def _fullname(self, name):
        return "%s%s.%s" % (self.prefix, name, self.base)

    def add_dns(self, name, ip):
        fn = self._fullname(name)
        input = "server %s\n" % (self.server)
        input += "zone %s\n" % (self.zone)
        input += "update add %s. %d A %s\n" % (fn, self.ltime, ip)
        input += "show\n"
        input += "send\n"
        self._run_command(['nsupdate', '-k', self.keyfile], input)

    def del_dns(self, name):
        fn = self._fullname(name)
        input = "server %s\n" % (self.server)
        input += "zone %s\n" % (self.zone)
        input += "update del %s.\n" % (fn)
        input += "show\n"
        input += "send\n"
        self._run_command(['nsupdate', '-k', self.keyfile], input)
