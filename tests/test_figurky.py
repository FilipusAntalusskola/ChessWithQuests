import unittest
from   model.figurka import *

class TestFigurky(unittest.TestCase):

    def test_kral(self):
        fig = Kral(1)
        self.assertEqual( fig.getBarvu( ), 1 )
        self.assertEqual( str(fig), 'K' )
        self.assertIn(    (1, 1), fig.getVektory( ) )
        self.assertIn(    (1, 0), fig.getVektory( ) )
        self.assertNotIn( (2, 1), fig.getVektory( ) )
        self.assertIn(    (1, 1), fig.getVektoryUtoku( ) )
        self.assertIn(    (1, 0), fig.getVektoryUtoku( ) )
        self.assertEqual( fig.getAllReachable( Pol(5,1), (8,8) ), { Pol(4,1), Pol(4,2), Pol(5,2), Pol(6,2), Pol(6,1) } )

    def test_dama(self):
        fig = Dama(-1)
        self.assertEqual( fig.getBarvu( ), -1 )
        self.assertEqual( str(fig), 'D' )
        self.assertEqual( fig.getNazev( ),    "Dáma" )
        self.assertIn(    (1, 1), fig.getVektory( ) )
        self.assertIn(    (1, 0), fig.getVektory( ) )
        self.assertNotIn( (2, 1), fig.getVektory( ) )
        self.assertIn(    (1, 1), fig.getVektoryUtoku( ) )
        self.assertIn(    (1, 0), fig.getVektoryUtoku( ) )
        self.assertNotIn( (2, 1), fig.getVektoryUtoku( ) )

    def test_strelec(self):
        fig = Strelec(1)
        self.assertEqual( fig.getBarvu( ), 1 )
        self.assertEqual( str(fig), 'S' )
        self.assertEqual( fig.getNazev( ),    "Střelec" )
        self.assertIn(    (1, 1), fig.getVektory( ) )
        self.assertNotIn( (1, 0), fig.getVektory( ) )
        self.assertNotIn( (2, 1), fig.getVektory( ) )
        self.assertIn(    (1, 1), fig.getVektoryUtoku( ) )
        self.assertNotIn( (1, 0), fig.getVektoryUtoku( ) )
        self.assertNotIn( (2, 1), fig.getVektoryUtoku( ) )

    def test_vez(self):
        fig = Vez(1)
        self.assertEqual( fig.getBarvu( ), 1 )
        self.assertEqual( str(fig), 'V' )
        self.assertNotIn( (1, 1), fig.getVektory( ) )
        self.assertIn(    (1, 0), fig.getVektory( ) )
        self.assertNotIn( (2, 1), fig.getVektory( ) )
        self.assertNotIn( (1, 1), fig.getVektoryUtoku( ) )
        self.assertIn(    (1, 0), fig.getVektoryUtoku( ) )
        self.assertNotIn( (2, 1), fig.getVektoryUtoku( ) )

    def test_kun(self):
        fig = Kun(1)
        self.assertEqual( fig.getBarvu( ), 1 )
        self.assertEqual( str(fig), 'J' )
        self.assertNotIn( (1, 1), fig.getVektory( ) )
        self.assertNotIn( (1, 0), fig.getVektory( ) )
        self.assertIn(    (2, 1), fig.getVektory( ) )
        self.assertNotIn( (1, 1), fig.getVektoryUtoku( ) )
        self.assertNotIn( (1, 0), fig.getVektoryUtoku( ) )
        self.assertIn(    (2, 1), fig.getVektoryUtoku( ) )
        self.assertEqual( fig.getAllReachable( Pol(2,1), (8,8) ), { Pol(1,3), Pol(3,3), Pol(4,2) } )

    def test_pesak(self):
        fig = Pesak(1)
        self.assertEqual( fig.getBarvu( ), 1 )
        self.assertEqual( str(fig),           'P' )
        self.assertEqual( fig.getNazev( ),    "Pěšec" )
        self.assertEqual( fig.getVektory( ), [ (0, 1) ] )
        self.assertEqual( fig.getVektoryUtoku( ), [ (1, 1), (-1, 1) ] )
        self.assertEqual( fig.getMoveRange( ), { 1,2 } )
        # Útok pěšce má nově vlastní rozsah {barva}, takže (4,4) už mezi kandidáty není.
        self.assertEqual( fig.getAllReachable( Pol(2,2), (8,8) ), { Pol(2,3), Pol(2,4), Pol(1,3), Pol(3,3) } )
        fig.setMoved( )
        self.assertEqual( fig.getVektory( ), [ (0, 1) ] )
        self.assertEqual( fig.getVektoryUtoku( ), [ (1, 1), (-1, 1) ] )
        self.assertEqual( fig.getMoveRange( ), { 1 } )
        self.assertEqual( fig.getAllReachable( Pol(2,2), (8,8) ), { Pol(2,3), Pol(1,3), Pol(3,3) } )

        fig = Pesak(-1)
        self.assertEqual( fig.getBarvu( ), -1 )
        self.assertEqual( str(fig), 'P' )
        self.assertEqual( fig.getVektory( ), [ (0, 1) ] )
        self.assertEqual( fig.getVektoryUtoku( ), [ (1, 1), (-1, 1) ] )
        self.assertEqual( fig.getMoveRange( ), { -1,-2 } )
        fig.setMoved( )
        self.assertEqual( fig.getVektory( ), [ (0, 1) ] )
        self.assertEqual( fig.getVektoryUtoku( ), [ (1, 1), (-1, 1) ] )
        self.assertEqual( fig.getMoveRange( ), { -1 } )

if __name__ == '__main__':
    unittest.main( )

