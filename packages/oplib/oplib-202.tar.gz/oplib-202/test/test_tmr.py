# This file is placed in the Public Domain.


"timer"


import unittest


from op.tmr import Timer


def test(event):
    pass


class Test_Timer(unittest.TestCase):

    def test_constructTimer(self):
        t = Timer(60, test)
        self.assertEqual(type(t), Timer)
