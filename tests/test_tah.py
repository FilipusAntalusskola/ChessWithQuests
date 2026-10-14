import unittest
from   model.figurka import *
from   model.pol     import Pol
from   model.tah     import Tah

class TestTah(unittest.TestCase):

    def test_tah_code(self):
        self.assertEqual( str( Tah( Pol(3,3), Pol(3,4), None    ) ), "?c3c4" )
        self.assertEqual( str( Tah( Pol(1,1), Pol(7,7), Dama(1) ) ), "Da1g7" )
        self.assertEqual( str( Tah( Pol(3,1), Pol(4,6), Vez(-1) ) ), "Vc1d6" )
        self.assertEqual( str( Tah( Pol(1,7), Pol(1,8), Pesak(1), Strelec(1) ) ), "Pa7a8S" )
        self.assertEqual( str( Tah( Pol(1,7), Pol(1,8), Pesak(1), Strelec(1) ).getNahradu( ) ), "S" )

if __name__ == '__main__':
    unittest.main( )

