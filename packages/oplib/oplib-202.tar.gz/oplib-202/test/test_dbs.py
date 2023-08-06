# This file is placed in the Public Domain.


"databases"


import unittest


from op.dbs import Db


class Test_Dbs(unittest.TestCase):

    def test_constructDb(self):
        db = Db()
        self.assertEqual(type(db), Db)
