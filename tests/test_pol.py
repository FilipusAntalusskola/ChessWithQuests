import unittest
from   model.pol import Pol

class TestPol(unittest.TestCase):

    def test_code(self):
        p = Pol(3,4)
        self.assertEqual( str(p),          "c4" )
        self.assertEqual( str(Pol(1,1)),   "a1" )
        self.assertEqual( str(Pol(8,8)),   "h8" )
        self.assertEqual( p.getSloupec( ), 3 )
        self.assertEqual( p.getRad( ),     4 )
        q = Pol(3,4)
        self.assertEqual( p, q )

if __name__ == '__main__':
    unittest.main( )

