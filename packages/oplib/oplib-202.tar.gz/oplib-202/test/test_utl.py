# This file is placed in the Public Domain.


"utility"


import unittest


from op.utl import spl


class Test_Utility(unittest.TestCase):

    def test_spl(self):
        a = "1,2,3"
        self.assertEqual(spl(a), ["1", "2", "3"])
