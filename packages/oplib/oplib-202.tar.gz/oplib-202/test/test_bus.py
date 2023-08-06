# This file is placed in the Public Domain.


"bus"


import unittest


from op.bus import Bus


class Test_Bus(unittest.TestCase):

    def test_constructBus(self):
        b = Bus()
        self.assertEqual(type(b), Bus)
