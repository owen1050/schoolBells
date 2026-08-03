import unittest, sys
from databaseQuerys import databaseQuerys

class TestDBCalls(unittest.TestCase):
    db = databaseQuerys("test.db")

    def test_default(self):
        self.assertEqual(0,0)

    def test_upCheck(self):
        self.assertEqual(self.db.dbCheck(), {'status': '0'})
 

if __name__ == '__main__':
    
    sys.argv.append('-v')
    unittest.main()