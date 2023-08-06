# This file is placed in the Public Domain.


"event"


import unittest


from op.evt import Event


class Test_Event(unittest.TestCase):

    def test_constructEvent(self):
        e = Event()
        self.assertEqual(type(e), Event)
