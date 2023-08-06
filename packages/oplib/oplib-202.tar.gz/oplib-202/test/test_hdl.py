# This file is placed in the Public Domain.


"handler"


import unittest


from op.hdl import Handler


class Test_Handler(unittest.TestCase):

    def test_constructHandler(self):
        h = Handler()
        self.assertEqual(type(h), Handler)
