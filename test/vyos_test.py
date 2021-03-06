#
# See LICENSE for full text.

import unittest
from nersc_sdn import vyos_interface


class VyosTestCase(unittest.TestCase):

    def setUp(self):
        self.vyos = vyos_interface.vyosInterface("sdn")

    def read_output(self):
        with open('ssh.out') as f:
            commands = f.read()
        return commands

    def test_add_nat(self):
        self.vyos.add_nat("172.17.0.17", "router", "1.2.3.4")
        commands = self.read_output()
        text = "set nat destination rule 44 translation address '172.17.0.17'"
        self.assertIn(text, commands)

    def test_remove_nat(self):
        self.vyos.remove_nat("router", "1.2.3.4")

    def test_key(self):
        """
        Make sure key gets passed through (ssh tester will say yep)
        """
        vyos = vyos_interface.vyosInterface("sdn", key='/etc/hosts')
        self.assertEqual(vyos.key, '/etc/hosts')
        vyos.add_nat("172.17.0.17", "router", "1.2.3.4")
        self.assertIn('yep', self.read_output())


if __name__ == '__main__':
    unittest.main()
