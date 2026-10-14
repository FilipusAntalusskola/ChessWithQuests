import unittest
from   model.figurka     import *
from   model.herni_plocha import HerniPlocha
from   model.pol         import Pol
from   model.revizor_tahu import RevizorTahu
from   model.tah         import Tah

class TestRevizorTahu(unittest.TestCase):

    def setUp(self):
        self.plocha = HerniPlocha( ).populateDefault( )

    def test_tah(self):
        # Nic
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(4,4), Pol(5,5) ) )
        self.assertIsNone( rev.tah )
        # Kůň
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,1), Pol(3,3) ) )
        self.assertTrue( rev.simulate_move( ) )
        self.assertTrue( rev.proved_tah( ) )
        self.assertFalse( rev.simulate_move( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(3,3), Pol(5,4) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,4), Pol(3,3) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(3,3), Pol(2,1) ) )
        self.assertTrue( rev.proved_tah( ) )
        # Pěšák
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(1,2), Pol(1,4) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,2), Pol(2,3) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,3), Pol(2,5) ) )
        self.assertFalse( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,3), Pol(2,4) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,4), Pol(2,5) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,5), Pol(2,6) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,6), Pol(2,7) ) )
        self.assertFalse( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,6), Pol(1,7) ) )
        self.assertTrue( rev.proved_tah( ) )
        self.assertEqual( [ str(fig) for fig in self.plocha.getVyhozeneFigurky(-1) ], [ 'P' ] )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(4,2), Pol(4,5) ) )
        self.assertFalse( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(3,2), Pol(3,3) ) )
        self.assertTrue( rev.proved_tah( ) )
        print(self.plocha)
        # Věž
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(1,1), Pol(1,3) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(1,3), Pol(1,4) ) )
        self.assertFalse( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(1,3), Pol(8,3) ) )
        self.assertFalse( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(3,3), Pol(3,4) ) ) # Pěšák
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(1,3), Pol(8,3) ) )
        self.assertTrue( rev.proved_tah( ) )
        # Střelec
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(3,1), Pol(1,3) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(1,3), Pol(5,7) ) )
        self.assertTrue( rev.proved_tah( ) )
        # Dáma
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(4,1), Pol(2,3) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,3), Pol(8,3) ) )
        self.assertFalse( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,3), Pol(7,3) ) )
        self.assertTrue( rev.proved_tah( ) )
        # Král
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(3,1) ) )
        self.assertFalse( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(4,1) ) )
        self.assertTrue( rev.proved_tah( ) )
        # Černý Král
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,8), Pol(5,7) ) )
        self.assertTrue( rev.proved_tah( ) )
        # Černý Pěšák
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(6,7), Pol(6,5) ) )
        self.assertTrue( rev.proved_tah( ) )


class TestRosada(unittest.TestCase):

    def setUp(self):
        self.plocha = HerniPlocha( )
        self.plocha.setFigurku( Kral(1), Pol(5,1) )
        self.plocha.setFigurku( Vez(1),  Pol(1,1) )
        self.plocha.setFigurku( Vez(1),  Pol(8,1) )

    def test_kratka00(self):
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(7,1) ) )
        self.assertTrue( rev.proved_tah( ) )
        self.assertIsInstance( self.plocha.vrat_obsah( Pol(6,1) ), Vez )

    def test_kratka01a(self):
        self.plocha.delFigurku( Pol(8,1) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(7,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_kratka01b(self):
        self.plocha.delFigurku( Pol(1,1) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(7,1) ) )
        self.assertTrue( rev.proved_tah( ) )

    def test_kratka02a(self):
        self.plocha.setFigurku( Dama(-1), Pol(5,8) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(7,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_kratka02b(self):
        self.plocha.setFigurku( Dama(-1), Pol(6,8) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(7,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_kratka03a(self):
        self.plocha.setFigurku( Kun(1), Pol(7,1) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(7,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_kratka03b(self):
        self.plocha.setFigurku( Strelec(-1), Pol(6,1) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(7,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_kratka04a(self):
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(6,1 ) ) ).proved_tah( )
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(6,1), Pol(5,1 ) ) ).proved_tah( )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(7,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_kratka04b(self):
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(8,1), Pol(7,1 ) ) ).proved_tah( )
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(7,1), Pol(8,1 ) ) ).proved_tah( )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(7,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_kratka04c(self):
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(1,1), Pol(2,1 ) ) ).proved_tah( )
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,1), Pol(1,1 ) ) ).proved_tah( )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(7,1) ) )
        self.assertTrue( rev.proved_tah( ) )

    def test_dlouha00(self):
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(3,1) ) )
        self.assertTrue( rev.proved_tah( ) )
        self.assertIsInstance( self.plocha.vrat_obsah( Pol(4,1) ), Vez )

    def test_dlouha01a(self):
        self.plocha.delFigurku( Pol(1,1) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(3,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_dlouha01b(self):
        self.plocha.delFigurku( Pol(8,1) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(3,1) ) )
        self.assertTrue( rev.proved_tah( ) )

    def test_dlouha02a(self):
        self.plocha.setFigurku( Dama(-1), Pol(5,8) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(3,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_dlouha02b(self):
        self.plocha.setFigurku( Dama(-1), Pol(4,8) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(3,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_dlouha02c(self):
        self.plocha.setFigurku( Dama(-1), Pol(3,8) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(3,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_dlouha03a(self):
        self.plocha.setFigurku( Kun(1), Pol(2,1) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(3,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_dlouha03b(self):
        self.plocha.setFigurku( Strelec(-1), Pol(3,1) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(3,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_dlouha03c(self):
        self.plocha.setFigurku( Dama(1), Pol(4,1) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(3,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_dlouha04a(self):
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(6,1) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(6,1), Pol(5,1) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(3,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_dlouha04b(self):
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(1,1), Pol(2,1) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(1,1), Pol(1,1) ) )
        self.assertFalse( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(3,1) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_dlouha04c(self):
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(8,1), Pol(7,1) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(7,1), Pol(8,1) ) )
        self.assertTrue( rev.proved_tah( ) )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(5,1), Pol(3,1) ) )
        self.assertTrue( rev.proved_tah( ) )


class TestEnPassant(unittest.TestCase):

    def setUp(self):
        self.plocha = HerniPlocha( ).populateDefault( )
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,7), Pol(2,5) ) ).proved_tah( )
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,5), Pol(2,4) ) ).proved_tah( )

    def test_enpassant01(self):
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(1,2), Pol(1,4) ) ).proved_tah( )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,4), Pol(1,3) ) )
        self.assertTrue( rev.proved_tah( ) )

    def test_enpassant02(self):
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(3,2), Pol(3,4) ) ).proved_tah( )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,4), Pol(3,3) ) )
        self.assertTrue( rev.proved_tah( ) )

    def test_enpassant03(self):
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,4), Pol(3,3) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_enpassant04(self):
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(3,2), Pol(3,4) ) ).proved_tah( )
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(7,2), Pol(7,3) ) ).proved_tah( )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,4), Pol(3,3) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_enpassant05(self):
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(3,2), Pol(3,3) ) ).proved_tah( )
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(3,3), Pol(3,4) ) ).proved_tah( )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,4), Pol(3,3) ) )
        self.assertFalse( rev.proved_tah( ) )

    def test_enpassant06(self):
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,4), Pol(2,3) ) ).proved_tah( )
        RevizorTahu( self.plocha, self.plocha.createTah( Pol(3,2), Pol(3,3) ) ).proved_tah( )
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(2,3), Pol(3,2) ) )
        self.assertFalse( rev.proved_tah( ) )


class TestNahradu(unittest.TestCase):

    def setUp(self):
        self.plocha = HerniPlocha( )
        self.plocha.setFigurku( Kral( 1), Pol(5,1) )
        self.plocha.setFigurku( Kral(-1), Pol(5,8) )
        self.plocha.setFigurku( Pesak(1), Pol(1,7) )

    def test_nahradu(self):
        rev = RevizorTahu( self.plocha, self.plocha.createTah( Pol(1,7), Pol(1,8), Dama(1) ) )
        self.assertTrue( rev.proved_tah( ) )

if __name__ == '__main__':
    unittest.main( )

