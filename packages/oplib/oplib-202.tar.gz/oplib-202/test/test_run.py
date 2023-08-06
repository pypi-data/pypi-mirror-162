# This file is placed in the Public Domain.


"run"


import unittest


from op.run import Commands


class Test_Commands(unittest.TestCase):

    def test_constructCommands(self):
        c = Commands()
        self.assertEqual(type(c), Commands)
