from __future__ import annotations

import copy
from model.figurka import Figurka, Kral, Pesak, VESTAVENE_TRIDY
from model.pol import Pol
from model.tah import Tah

MIN_SIRKA, MAX_SIRKA = 4, 16
MIN_VYSKA, MAX_VYSKA = 5, 16


def vychozi_rada(sirka: int) -> str:
    """Vygeneruje základní řadu pro libovolnou šířku. Pro 8 sloupců dává klasické VJSDKSJV."""
    vzor = "VJS" + "JS" * 10
    vlevo = (sirka - 2) // 2
    vpravo = sirka - 2 - vlevo
    return vzor[:vlevo] + "DK" + vzor[:vpravo][::-1]


class Herni_Plocha:
    # Šachovnice libovolné velikosti; uchovává rozmístění figurek.

    def __init__(self, rozmery=(8, 8)):
        self.rozmery = int(rozmery[0]), int(rozmery[1])     # (šířka, výška) – tuple, ne Pol!
        self.herni_deska: list[list[Figurka | None]] = [[None] * self.rozmery[1] for _ in range(self.rozmery[0])]
        self.pred_tah: Tah | None = None
        self.vyhozene_figurky_b: list[Figurka] = []      # vyhozené bílé figurky
        self.vyhozene_figurky_c: list[Figurka] = []      # vyhozené černé figurky

    def __str__(self):
        deska = ''
        for rad in range(self.rozmery[1], 0, -1):
            deska += f"{rad:>2} "
            for sloupec in range(1, self.rozmery[0] + 1):
                fig = self.vrat_obsah(Pol(sloupec, rad))
                if fig is None:
                    kod = '.'
                else:
                    kod = str(fig)
                    kod = kod.upper() if fig.getBarvu() == 1 else kod.lower()
                deska += kod
            deska += "\n"
        deska += "   " + "".join(chr(97 + i) for i in range(self.rozmery[0])) + "\n"
        return deska

    def copy(self):
        return copy.deepcopy(self)

    def kopie_rychla(self) -> "Herni_Plocha":
        # Mělká kopie pro simulaci tahů: nová mřížka, stejné objekty figurek.
        # Figurky se při simulaci nemění (RevizorTahu.proved_tah(oznac=False)).
        p = Herni_Plocha.__new__(Herni_Plocha)
        p.rozmery = self.rozmery
        p.herni_deska = [sloupec[:] for sloupec in self.herni_deska]
        p.pred_tah = self.pred_tah
        p.vyhozene_figurky_b = []
        p.vyhozene_figurky_c = []
        return p

    # --- základní operace ---
    def createTah(self, vychozi_pozice: Pol, cilova_pozice: Pol, nahrad: Figurka | None = None) -> Tah | None:
        if not self.checkSouradnici(vychozi_pozice):
            return None
        fig = self.vrat_obsah(vychozi_pozice)
        if fig is None:
            return None
        return Tah(vychozi_pozice, cilova_pozice, fig, nahrad)

    def vrat_obsah(self, pozice: Pol) -> Figurka | None:
        if not self.checkSouradnici(pozice):
            return None
        return self.herni_deska[pozice.getSloupec() - 1][pozice.getRad() - 1]

    def setFigurku(self, fig: Figurka | None, pozice: Pol) -> Figurka | None:
        if self.checkSouradnici(pozice):
            self.herni_deska[pozice.getSloupec() - 1][pozice.getRad() - 1] = fig
        return fig

    def poloz_figurku(self, figurka: Figurka, pozice: Pol) -> Figurka:
        # název z původní verze (4)
        return self.setFigurku(figurka, pozice)

    def delFigurku(self, pozice: Pol) -> Figurka | None:
        if self.checkSouradnici(pozice):
            deadfig = self.vrat_obsah(pozice)
            self.setFigurku(None, pozice)
            return deadfig
        return None

    def setPredTah(self, tah: Tah) -> Tah:
        self.pred_tah = tah
        return tah

    def getPredTah(self) -> Tah | None:
        return self.pred_tah

    def getHerniDeska(self) -> list[list[Figurka | None]]:
        return self.herni_deska

    def checkSouradnici(self, pozice: Pol) -> bool:
        return 1 <= pozice.getSloupec() <= self.rozmery[0] and 1 <= pozice.getRad() <= self.rozmery[1]

    def isFigurka(self, pozice: Pol) -> bool:
        return self.vrat_obsah(pozice) is not None

    def figurky(self, barva: int = 0):
        # Generátor (Pol, Figurka) přes všechny figurky dané barvy (0 = obě barvy)
        for x in range(1, self.rozmery[0] + 1):
            for y in range(1, self.rozmery[1] + 1):
                fig = self.herni_deska[x - 1][y - 1]
                if fig is not None and (barva == 0 or fig.getBarvu() == barva):
                    yield Pol(x, y), fig

    # --- rozestavení ---
    def populate(self, rada: str, registr=None, pesci: bool = True) -> "Herni_Plocha":
        """Rozestaví figurky. `rada` je řetězec značek pro 1. řadu (např. 'VJSDKSJV'),
        černý ji má zrcadlově nahoře. `registr` (RegistrFigurek) umí vytvořit i vlastní figurky."""
        sirka, vyska = self.rozmery
        if len(rada) != sirka:
            raise ValueError(f"Základní řada musí mít {sirka} znaků, má {len(rada)}.")

        def vytvor(znacka, barva):
            if registr is not None:
                return registr.vytvor(znacka, barva)
            return VESTAVENE_TRIDY[znacka.upper()](barva)

        for i, znacka in enumerate(rada.upper()):
            if znacka in ('.', '-', ' '):
                continue
            self.setFigurku(vytvor(znacka, 1), Pol(i + 1, 1))
            self.setFigurku(vytvor(znacka, -1), Pol(i + 1, vyska))
        if pesci:
            for i in range(sirka):
                self.setFigurku(Pesak(1), Pol(i + 1, 2))
                self.setFigurku(Pesak(-1), Pol(i + 1, vyska - 1))
        return self

    def populateDefault(self) -> "Herni_Plocha":
        return self.populate(vychozi_rada(self.rozmery[0]))

    # --- vyhozené figurky ---
    def getVyhozeneFigurky(self, barva: int) -> list[Figurka]:
        if barva == 1:
            return self.vyhozene_figurky_b
        if barva == -1:
            return self.vyhozene_figurky_c
        return []

    def addVyhozenouFigurku(self, fig: Figurka | None) -> Figurka | None:
        if fig is None:
            return None
        if fig.getBarvu() == 1:
            self.vyhozene_figurky_b.append(fig)
        else:
            self.vyhozene_figurky_c.append(fig)
        return fig

    # --- šach / mat / pat ---
    def checkOhrozeni(self, pozice: Pol, barvAttak: int) -> bool:
        # True, pokud některá figurka barvy barvAttak ohrožuje pole pozice.
        from model.revizor_tahu import RevizorTahu
        for start, fig in self.figurky(barvAttak):
            if start == pozice:
                continue
            if RevizorTahu(self, Tah(start, pozice, fig)).utoci():
                return True
        return False

    def najdi_krale(self, barva: int) -> Pol | None:
        for pol, fig in self.figurky(barva):
            if isinstance(fig, Kral):
                return pol
        return None

    def check_sach(self, barva: int = 0) -> int:
        # Vrátí barvu krále, který je v šachu; jinak 0.
        for b in ((1, -1) if barva == 0 else (barva,)):
            pol = self.najdi_krale(b)
            if pol is not None and self.checkOhrozeni(pol, -b):
                return b
        return 0

    def check_mat(self, barva: int) -> bool:
        return self._check_pat_a_mat(barva, True)

    def check_pat(self, barva: int) -> bool:
        return self._check_pat_a_mat(barva, False)

    def _kandidati(self, start: Pol, fig: Figurka):
        # Pole, kam by figurka mohla jít – včetně rošády u krále
        cile = fig.getAllReachable(start, self.rozmery)
        if isinstance(fig, Kral) and not fig.isMoved():
            for dx in (-2, 2):
                p = Pol(start.getSloupec() + dx, start.getRad())
                if self.checkSouradnici(p):
                    cile.add(p)
        return cile

    def getLegalMovesFrom(self, start: Pol) -> list[Tah]:
        # Všechny platné tahy figurky na poli start.
        from model.revizor_tahu import RevizorTahu
        fig = self.vrat_obsah(start)
        if fig is None:
            return []
        tahy = []
        for cil in self._kandidati(start, fig):
            tah = Tah(start, cil, fig)
            rev = RevizorTahu(self, tah)
            if (rev.precheckmove() or rev.checkEnPassant() or rev.checkRosadu()) and rev.simulate_move():
                tahy.append(tah)
        return tahy

    def getAllLegalMoves(self, barva: int) -> list[Tah]:
        tahy = []
        for start, _ in list(self.figurky(barva)):
            tahy.extend(self.getLegalMovesFrom(start))
        return tahy

    def ma_platny_tah(self, barva: int) -> bool:
        from model.revizor_tahu import RevizorTahu
        for start, fig in list(self.figurky(barva)):
            for cil in self._kandidati(start, fig):
                rev = RevizorTahu(self, Tah(start, cil, fig))
                if (rev.precheckmove() or rev.checkEnPassant() or rev.checkRosadu()) and rev.simulate_move():
                    return True
        return False

    def _check_pat_a_mat(self, barva: int, check_for_mat: bool) -> bool:
        v_sachu = self.check_sach(barva) == barva
        if check_for_mat != v_sachu:
            return False
        return not self.ma_platny_tah(barva)


HerniPlocha = Herni_Plocha   # jméno z projektu (3)


if __name__ == '__main__':
    plocha = Herni_Plocha().populateDefault()
    print(plocha)
    print(vychozi_rada(10), vychozi_rada(6))
