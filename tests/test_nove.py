"""Testy funkcí přidaných při převodu do nové verze."""
import io
import unittest
from pathlib import Path

from model.definice_figurek import RegistrFigurek, parse_pohyby, format_pohyby
from model.figurka import Kral, Vez, Pesak, Dama
from model.game_manager import GameManager, MAT, VZDANO
from model.herni_plocha import Herni_Plocha, vychozi_rada
from model.hrac import Hrac
from model.kwest_manager import KwestKatalog, KwestManager
from model.pol import Pol
from model.revizor_tahu import RevizorTahu
from model.uzivatel import Uzivatel
from model.user_manager import UserManager

DATA = Path(__file__).resolve().parent.parent / "data"


class TestDefinovaneFigurky(unittest.TestCase):
    def setUp(self):
        self.reg = RegistrFigurek(DATA / "figurky.json")

    def test_parse(self):
        p = parse_pohyby("1,1 1,-1\n1,2 2,1 ; 1\n0,1 ; 0 ; vpřed")
        self.assertEqual(len(p), 3)
        self.assertEqual(p[1].dosah, 1)
        self.assertTrue(p[2].vpred)
        self.assertEqual(parse_pohyby(format_pohyby(p)), p)
        with self.assertRaises(ValueError):
            parse_pohyby("0,0")
        with self.assertRaises(ValueError):
            parse_pohyby("1;2")

    def test_arcibiskup(self):
        plocha = Herni_Plocha()
        a = self.reg.vytvor('A', 1)
        plocha.setFigurku(a, Pol(4, 4))
        plocha.setFigurku(Kral(1), Pol(1, 1))
        plocha.setFigurku(Kral(-1), Pol(8, 8))
        cile = {t.getCil() for t in plocha.getLegalMovesFrom(Pol(4, 4))}
        self.assertIn(Pol(5, 6), cile)      # jezdec
        self.assertIn(Pol(7, 7), cile)      # střelec
        self.assertNotIn(Pol(4, 5), cile)   # rovně ne
        self.assertNotIn(Pol(6, 8), cile)   # jezdec jen o 1 krok

    def test_kopinik_jen_vpred(self):
        plocha = Herni_Plocha()
        plocha.setFigurku(Kral(1), Pol(1, 1))
        plocha.setFigurku(Kral(-1), Pol(8, 8))
        plocha.setFigurku(self.reg.vytvor('L', 1), Pol(3, 3))
        plocha.setFigurku(self.reg.vytvor('L', -1), Pol(6, 6))
        bile = {t.getCil() for t in plocha.getLegalMovesFrom(Pol(3, 3))}
        cerne = {t.getCil() for t in plocha.getLegalMovesFrom(Pol(6, 6))}
        self.assertEqual(bile, {Pol(3, y) for y in range(4, 9)})
        self.assertEqual(cerne, {Pol(6, y) for y in range(1, 6)})

    def test_zabak_preskakuje(self):
        plocha = Herni_Plocha()
        plocha.setFigurku(Kral(1), Pol(1, 1))
        plocha.setFigurku(Kral(-1), Pol(8, 8))
        plocha.setFigurku(self.reg.vytvor('Z', 1), Pol(4, 4))
        plocha.setFigurku(Pesak(1), Pol(4, 5))
        cile = {t.getCil() for t in plocha.getLegalMovesFrom(Pol(4, 4))}
        self.assertIn(Pol(4, 6), cile)
        self.assertNotIn(Pol(4, 5), cile)

    def test_vlastni_figurka_dava_sach(self):
        plocha = Herni_Plocha()
        plocha.setFigurku(Kral(1), Pol(1, 1))
        plocha.setFigurku(Kral(-1), Pol(5, 5))
        plocha.setFigurku(self.reg.vytvor('U', 1), Pol(4, 2))   # velbloud 1,3
        self.assertEqual(plocha.check_sach(-1), -1)


class TestVelikostDesky(unittest.TestCase):
    def test_vychozi_rada(self):
        self.assertEqual(vychozi_rada(8), "VJSDKSJV")
        for w in range(4, 17):
            r = vychozi_rada(w)
            self.assertEqual(len(r), w)
            self.assertEqual(r.count('K'), 1)

    def test_ruzne_velikosti(self):
        for w, h in [(4, 5), (6, 6), (10, 8), (12, 12), (16, 16)]:
            p = Herni_Plocha((w, h)).populateDefault()
            self.assertEqual(p.check_sach(), 0)
            self.assertGreater(len(p.getAllLegalMoves(1)), 0)
            self.assertGreater(len(p.getAllLegalMoves(-1)), 0)

    def test_rosada_na_siroke_desce(self):
        p = Herni_Plocha((10, 8))
        p.setFigurku(Kral(1), Pol(6, 1))
        p.setFigurku(Vez(1), Pol(1, 1))
        p.setFigurku(Vez(1), Pol(10, 1))
        p.setFigurku(Kral(-1), Pol(6, 8))
        self.assertTrue(RevizorTahu(p, p.createTah(Pol(6, 1), Pol(8, 1))).proved_tah())
        self.assertIsInstance(p.vrat_obsah(Pol(7, 1)), Vez)
        self.assertIsNone(p.vrat_obsah(Pol(10, 1)))

    def test_nove_moznosti_rosady_v_seznamu(self):
        p = Herni_Plocha()
        p.setFigurku(Kral(1), Pol(5, 1))
        p.setFigurku(Vez(1), Pol(8, 1))
        p.setFigurku(Kral(-1), Pol(5, 8))
        self.assertIn(Pol(7, 1), {t.getCil() for t in p.getLegalMovesFrom(Pol(5, 1))})

    def test_en_passant_jen_sousedni(self):
        # V (3) mohl pěšec "brát mimochodem" odkudkoli – teď už ne.
        p = Herni_Plocha().populateDefault()
        for a, b in [((5, 2), (5, 4)), ((1, 7), (1, 6)), ((5, 4), (5, 5)), ((4, 7), (4, 5))]:
            self.assertTrue(RevizorTahu(p, p.createTah(Pol(*a), Pol(*b))).proved_tah())
        self.assertTrue(RevizorTahu(p, p.createTah(Pol(5, 5), Pol(4, 6))).simulate_move())
        self.assertFalse(RevizorTahu(p, p.createTah(Pol(8, 2), Pol(4, 6))).simulate_move())

    def test_pat(self):
        p = Herni_Plocha()
        p.setFigurku(Kral(-1), Pol(1, 8))
        p.setFigurku(Kral(1), Pol(2, 6))
        p.setFigurku(Dama(1), Pol(4, 7))
        tah = p.createTah(Pol(4, 7), Pol(3, 7))
        self.assertTrue(RevizorTahu(p, tah).proved_tah())
        self.assertTrue(tah.pat)
        self.assertFalse(tah.mat)


class TestPartie(unittest.TestCase):
    def setUp(self):
        self.kat = KwestKatalog(DATA / "kwesty.json")
        self.km = KwestManager(self.kat.kwesty)
        self.reg = RegistrFigurek(DATA / "figurky.json")
        hraci = [Hrac(1, Uzivatel("Anna")), Hrac(-1, Uzivatel("Bob"))]
        self.gm = GameManager(Herni_Plocha().populateDefault(), hraci, self.km, registr=self.reg)

    def tahni(self, a, b, nahrad=None):
        return self.gm.proved_tah(Pol(*a), Pol(*b), nahrad)

    def test_ovci_mat(self):
        self.assertIsNotNone(self.tahni((6, 2), (6, 3)))
        self.assertIsNone(self.tahni((6, 3), (6, 4)))      # černý je na tahu
        self.tahni((5, 7), (5, 5))
        self.tahni((7, 2), (7, 4))
        v = self.tahni((4, 8), (8, 4))
        self.assertTrue(v.tah.mat)
        self.assertTrue(v.konec)
        self.assertEqual(self.gm.get_stav(), MAT)
        self.assertEqual(self.gm.vysledek_pgn(), "0-1")
        ids = {k.id for _, k in v.nove_kwesty}
        self.assertIn("sach_mat", ids)
        self.assertIn("vitez", ids)
        self.assertIn("bleskova_vyhra", ids)
        out = io.StringIO()
        self.gm.export_pgn(out)
        self.assertIn("2. g4 Qh4#", out.getvalue())
        self.assertIn('[Result "0-1"]', out.getvalue())

    def test_tah_zpet(self):
        self.tahni((5, 2), (5, 4))
        self.assertIn("prvni_krok", self.km.splnene_ted[0])
        self.assertTrue(self.gm.zrus_tah())
        self.assertEqual(self.gm.aktivni_hrac, 0)
        self.assertIsNotNone(self.gm.plocha.vrat_obsah(Pol(5, 2)))
        self.assertNotIn("prvni_krok", self.km.splnene_ted[0])
        self.assertFalse(self.gm.zrus_tah())

    def test_promena_vyzaduje_volbu(self):
        p = Herni_Plocha()
        p.setFigurku(Kral(1), Pol(5, 1))
        p.setFigurku(Kral(-1), Pol(8, 8))
        p.setFigurku(Pesak(1), Pol(1, 7))
        gm = GameManager(p, self.gm.hraci, KwestManager(self.kat.kwesty), registr=self.reg)
        self.assertTrue(gm.vyzaduje_promenu(Pol(1, 7), Pol(1, 8)))
        self.assertIsNone(gm.proved_tah(Pol(1, 7), Pol(1, 8)))
        v = gm.proved_tah(Pol(1, 7), Pol(1, 8), 'D')
        self.assertIsInstance(gm.plocha.vrat_obsah(Pol(1, 8)), Dama)
        self.assertIn("karierni_postup", {k.id for _, k in v.nove_kwesty})
        # proměna ve vlastní figurku
        p2 = Herni_Plocha()
        p2.setFigurku(Kral(1), Pol(5, 1))
        p2.setFigurku(Kral(-1), Pol(8, 8))
        p2.setFigurku(Pesak(1), Pol(1, 7))
        gm2 = GameManager(p2, self.gm.hraci, registr=self.reg)
        gm2.proved_tah(Pol(1, 7), Pol(1, 8), 'A')
        self.assertEqual(gm2.plocha.vrat_obsah(Pol(1, 8)).getNazev(), "Arcibiskup")

    def test_vzdani_a_elo(self):
        self.gm.vzdat(0)
        self.assertEqual(self.gm.get_stav(), VZDANO)
        self.assertEqual(self.gm.vitez, 1)
        um = UserManager(None)
        a, b = self.gm.hraci[0].uzivatel, self.gm.hraci[1].uzivatel
        d = um.zapis_vysledek(a, b, self.gm.skore_bileho())
        self.assertEqual(d, (-16, 16))
        self.assertEqual(b.vyhry, 1)

    def test_rozliseni_v_notaci(self):
        p = Herni_Plocha()
        p.setFigurku(Kral(1), Pol(5, 1))
        p.setFigurku(Kral(-1), Pol(5, 8))
        p.setFigurku(Vez(1), Pol(1, 4))
        p.setFigurku(Vez(1), Pol(8, 4))
        gm = GameManager(p, self.gm.hraci, registr=self.reg)
        gm.proved_tah(Pol(1, 4), Pol(4, 4))
        out = io.StringIO()
        gm.export_pgn(out)
        self.assertIn("1. Rad4", out.getvalue())


if __name__ == '__main__':
    unittest.main()
