# This file is placed in the Public Domain.


"thread"


import unittest


from op.thr import Thread


def test(event):
    pass


class Test_Thread(unittest.TestCase):

    def test_constructThread(self):
        t = Thread(test, "test")
        self.assertEqual(type(t), Thread)
