import unittest
from   model.herni_plocha import HerniPlocha
from   model.figurka     import *
from   model.pol         import Pol

class TestHerniPlocha(unittest.TestCase):

    def test_herni_plocha(self):
        plocha = HerniPlocha( ).populateDefault( )
        self.assertEqual(  plocha.vrat_obsah( Pol(4,1) ).getNazev( ), 'Dáma' )
        self.assertIs(     plocha.vrat_obsah( Pol(5,5) ), None )
        self.assertFalse(  plocha.isFigurka( Pol(5,5) ) )
        plocha.setFigurku( Pesak(1), Pol(5,5) )
        self.assertEqual(  plocha.vrat_obsah( Pol(5,5) ).getNazev( ), 'Pěšec' )
        self.assertTrue(   plocha.isFigurka( Pol(5,5) ) )
        plocha.delFigurku( Pol(5,5) )
        self.assertFalse(  plocha.isFigurka( Pol(5,5) ) )
        plocha2 = plocha.copy( )
        self.assertEqual( str(plocha), str(plocha2) )

    def test_sach(self):
        plocha = HerniPlocha( )
        plocha.setFigurku( Kral(1),   Pol(5,1) )
        plocha.setFigurku( Kral(-1),  Pol(1,8) )
        self.assertFalse(  plocha.check_sach( 1) )
        self.assertFalse(  plocha.check_sach(-1) )
        plocha.setFigurku( Dama(-1),  Pol(5,7) )
        self.assertTrue(   plocha.check_sach( 1) )
        plocha.setFigurku( Pesak(-1), Pol(5,4) )
        self.assertFalse(  plocha.check_sach( 1) )
        plocha.setFigurku( Pesak(1),  Pol(2,7) )
        self.assertTrue(   plocha.check_sach(-1) )
        self.assertFalse(  plocha.check_sach( 1) )

    def test_mat(self):
        plocha = HerniPlocha( )
        plocha.setFigurku( Kral(1),   Pol(5,1) )
        plocha.setFigurku( Kral(-1),  Pol(1,8) )
        self.assertFalse(  plocha.check_mat( 1) )
        self.assertFalse(  plocha.check_mat(-1) )
        plocha.setFigurku( Dama(-1),  Pol(5,7) )
        self.assertFalse(  plocha.check_mat(1) )
        plocha.delFigurku( Pol(5,7) )
        plocha.setFigurku( Dama(-1),  Pol(5,2) )
        self.assertFalse(  plocha.check_mat(1) )
        plocha.setFigurku( Vez(-1),   Pol(1,2) )
        self.assertTrue(   plocha.check_mat(1) )
        plocha.setFigurku( Vez(1),    Pol(5,8) )
        self.assertFalse(  plocha.check_mat(1) )
        """
        plocha = HerniPlocha( )
        plocha.setFigurku( Kral(1),   Pol(5,1) )
        plocha.setFigurku( Kral(-1),  Pol(1,8) )
        plocha.setFigurku( Dama(-1),  Pol(5,8) )
        plocha.setFigurku( Vez(-1),   Pol(4,8) )
        plocha.setFigurku( Dama(-1),  Pol(5,8) )
        plocha.setFigurku( Vez(-1),   Pol(6,8) )
        self.assertTrue(   plocha.check_mat(1) )
        plocha.setFigurku( Vez(1),    Pol(1,2) )
        self.assertFalse(  plocha.check_mat(1) )
        """

    def test_vyhozeny(self):
        plocha = HerniPlocha( )
        plocha.addVyhozenouFigurku( Dama(-1 ) )
        self.assertEqual( [ str(fig) for fig in plocha.getVyhozeneFigurky(-1) ], [ 'D' ] )

    def test_all_moves(self):
        plocha = HerniPlocha( ).populateDefault( )
        print( sorted([ str(tah) for tah in plocha.getAllLegalMoves(1) ] ) )
        self.assertEqual( sorted( [ str(tah) for tah in plocha.getAllLegalMoves(1) ] ),
                          [ 'Jb1a3', 'Jb1c3', 'Jg1f3', 'Jg1h3', 'Pa2a3', 'Pa2a4', 'Pb2b3',
                            'Pb2b4', 'Pc2c3', 'Pc2c4', 'Pd2d3', 'Pd2d4', 'Pe2e3', 'Pe2e4',
                            'Pf2f3', 'Pf2f4', 'Pg2g3', 'Pg2g4', 'Ph2h3', 'Ph2h4' ]
                        )


if __name__ == '__main__':
    unittest.main( )

