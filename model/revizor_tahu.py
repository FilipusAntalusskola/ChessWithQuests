from __future__ import annotations

from typing import TYPE_CHECKING

from model.figurka import Kral, Pesak, Vez
from model.pol import Pol
from model.tah import Tah

if TYPE_CHECKING:       # jen kvůli typovým nápovědám – řeší kruhový import z projektu (3)
    from model.herni_plocha import Herni_Plocha


class RevizorTahu:
    # Kontroluje platnost tahů a provádí je.

    def __init__(self, herni_plocha: "Herni_Plocha", tah: Tah | None):
        self.tah = tah
        self.herni_plocha = herni_plocha

    def __str__(self):
        return str(self.tah)

    def setTah(self, tah: Tah):
        self.tah = tah
        return self

    def getTah(self) -> Tah | None:
        return self.tah

    # ------------------------------------------------------------ geometrie tahu
    def getBaseVektor(self, utok: bool | None = None) -> tuple[int, int] | None:
        """Pokud tah odpovídá některému základnímu vektoru figurky (v povoleném rozsahu),
        vrátí jednotkový krok (se znaménkem). Jinak None.
        utok=None: útočné vektory se použijí, když na cíli stojí figurka (tak se chová pěšec)."""
        if self.tah is None:
            return None
        start, cil = self.tah.getStart(), self.tah.getCil()
        diff = (cil.getSloupec() - start.getSloupec(), cil.getRad() - start.getRad())
        if diff == (0, 0):
            return None
        fig = self.tah.getFigurku()
        if fig is None:
            return None
        if utok is None:
            utok = self.herni_plocha.isFigurka(cil)
        vektory = fig.getVektoryUtoku() if utok else fig.getVektory()
        normvektory = fig.getNormVektoryUtoku() if utok else fig.getNormVektory()

        # Kolinearitu zjistíme skalárním součinem s normálovým vektorem (= 0 → rovnoběžné).
        for i, base in enumerate(vektory):
            nx, ny = normvektory[i]
            if nx * diff[0] + ny * diff[1] != 0:
                continue
            # Násobek musí být celé číslo (jinak by např. vektor 2,2 "došel" na pole o 1,1)
            if base[1] != 0:
                if diff[1] % base[1] != 0:
                    continue
                mult = diff[1] // base[1]
            else:
                if diff[0] % base[0] != 0:
                    continue
                mult = diff[0] // base[0]
            if (base[0] * mult, base[1] * mult) != diff:
                continue
            rozsah = fig.getRozsah(i, utok)
            if rozsah is None:
                tmp = max(self.herni_plocha.rozmery) - 1
                lo, hi = -tmp, tmp
            else:
                lo, hi = min(rozsah), max(rozsah)
            if mult < lo or mult > hi:
                continue
            return base if mult > 0 else (-base[0], -base[1])
        return None

    def checkValidCil(self) -> bool:
        # True, pokud je cíl prázdný NEBO na něm stojí soupeřova figurka.
        fig = self.tah.getFigurku()
        if fig is None:
            return True
        other_fig = self.herni_plocha.vrat_obsah(self.tah.getCil())
        if other_fig is None:
            return True
        return fig.getBarvu() != other_fig.getBarvu()

    def isCistaCesta(self, baseVektor: tuple[int, int]) -> bool:
        # True, pokud je cesta mezi startem a cílem (bez krajních polí) volná.
        cil = self.tah.getCil()
        curpos = Pol(self.tah.getStart().getSloupec() + baseVektor[0], self.tah.getStart().getRad() + baseVektor[1])
        while curpos != cil:
            if not self.herni_plocha.checkSouradnici(curpos) or self.herni_plocha.isFigurka(curpos):
                return False
            curpos = Pol(curpos.getSloupec() + baseVektor[0], curpos.getRad() + baseVektor[1])
        return True

    def utoci(self) -> bool:
        # True, pokud figurka z tahu ohrožuje cílové pole (bez ohledu na to, co na něm stojí).
        if self.tah is None or self.tah.getFigurku() is None:
            return False
        base = self.getBaseVektor(utok=True)
        if base is None:
            return False
        return self.tah.getFigurku().skok or self.isCistaCesta(base)

    # ------------------------------------------------------------ speciální tahy
    def checkEnPassant(self) -> bool:
        # True, pokud jde o platné braní mimochodem.
        if self.tah is None:
            return False
        fig = self.tah.getFigurku()
        if not isinstance(fig, Pesak):
            return False
        pred_tah = self.herni_plocha.getPredTah()
        if pred_tah is None:
            return False
        pred_fig = pred_tah.getFigurku()
        if not isinstance(pred_fig, Pesak) or pred_fig.getBarvu() == fig.getBarvu():
            return False
        if abs(pred_tah.getStart().getRad() - pred_tah.getCil().getRad()) != 2:
            return False
        if self.herni_plocha.vrat_obsah(pred_tah.getCil()) is not pred_fig:
            return False
        if self.tah.getCil().getRad() != (pred_tah.getCil().getRad() + pred_tah.getStart().getRad()) // 2:
            return False
        if pred_tah.getStart().getSloupec() != self.tah.getCil().getSloupec():
            return False
        if self.herni_plocha.isFigurka(self.tah.getCil()):
            return False
        # Pěšec musí táhnout svým útočným vektorem (šikmo o 1) – v (3) tahle kontrola chyběla
        return self.getBaseVektor(utok=True) is not None

    def checkRosadu(self) -> bool:
        """Rošáda na desce libovolné šířky: král jde o 2 pole k věži v rohu,
        věž přeskočí na pole, přes které král přešel."""
        if self.tah is None:
            return False
        fig = self.tah.getFigurku()
        if not isinstance(fig, Kral) or fig.isMoved():
            return False
        start, cil = self.tah.getStart(), self.tah.getCil()
        if cil.getRad() != start.getRad():
            return False
        dx = cil.getSloupec() - start.getSloupec()
        if abs(dx) != 2:
            return False
        smer = 1 if dx > 0 else -1
        vez_x = self.herni_plocha.rozmery[0] if smer > 0 else 1
        if abs(vez_x - start.getSloupec()) < 3:
            return False
        rad = start.getRad()
        vez = self.herni_plocha.vrat_obsah(Pol(vez_x, rad))
        if not isinstance(vez, Vez) or vez.isMoved() or vez.getBarvu() != fig.getBarvu():
            return False
        for x in range(min(start.getSloupec(), vez_x) + 1, max(start.getSloupec(), vez_x)):
            if self.herni_plocha.isFigurka(Pol(x, rad)):
                return False
        for x in (start.getSloupec(), start.getSloupec() + smer, cil.getSloupec()):
            if self.herni_plocha.checkOhrozeni(Pol(x, rad), -fig.getBarvu()):
                return False
        return True

    # ------------------------------------------------------------ kontroly
    def precheckmove(self) -> bool:
        # True, pokud jde o platný "obyčejný" tah (včetně braní a proměny), bez en passant a rošády.
        if self.tah is None:
            return False
        plocha = self.herni_plocha
        if not plocha.checkSouradnici(self.tah.getStart()) or not plocha.checkSouradnici(self.tah.getCil()):
            return False
        if not plocha.isFigurka(self.tah.getStart()):
            return False
        if not self.checkValidCil():
            return False
        baseVektor = self.getBaseVektor()
        if baseVektor is None:
            return False
        if not self.tah.getFigurku().skok and not self.isCistaCesta(baseVektor):
            return False

        nahrad_fig = self.tah.getNahradu()
        if nahrad_fig is not None:
            orig_fig = plocha.vrat_obsah(self.tah.getStart())
            if not isinstance(orig_fig, Pesak):
                return False
            orig_barva = orig_fig.getBarvu()
            if orig_barva != nahrad_fig.getBarvu():
                return False
            if isinstance(nahrad_fig, (Kral, Pesak)):
                return False
            if not self.je_posledni_rada(self.tah.getCil(), orig_barva):
                return False
        return True

    def je_posledni_rada(self, pol: Pol, barva: int) -> bool:
        return (barva == 1 and pol.getRad() == self.herni_plocha.rozmery[1]) or (barva == -1 and pol.getRad() == 1)

    def postcheckmove(self) -> bool:
        # True, pokud král hráče, který táhl, NENÍ po tahu v šachu.
        fig = self.tah.getFigurku()
        if fig is None:
            return True
        barva = fig.getBarvu()
        kral = self.herni_plocha.najdi_krale(barva)
        if kral is None:
            return True
        return not self.herni_plocha.checkOhrozeni(kral, -barva)

    def simulate_move(self) -> bool:
        # Zjistí, zda by tah byl platný; nic nemění.
        rev2 = RevizorTahu(self.herni_plocha.kopie_rychla(), self.tah)
        return rev2.proved_tah(oznac=False)

    # ------------------------------------------------------------ provedení
    def proved_tah(self, oznac: bool = True) -> bool:
        """Provede tah, je-li platný (vrací True). Jinak stav nezmění a vrátí False.
        oznac=False se používá při simulaci: nemění figurky a nepočítá šach/mat."""
        if self.tah is None:
            return False
        plocha = self.herni_plocha
        start, cil = self.tah.getStart(), self.tah.getCil()
        isenpassant = False
        isrosada = False
        deadfig = None
        predTah = None
        vez = None

        if self.precheckmove():
            deadfig = plocha.delFigurku(cil)
            plocha.setFigurku(plocha.delFigurku(start), cil)
        elif self.checkEnPassant():
            predTah = plocha.getPredTah()
            deadfig = plocha.delFigurku(predTah.getCil())
            plocha.setFigurku(plocha.delFigurku(start), cil)
            isenpassant = True
        elif self.checkRosadu():
            smer = 1 if cil.getSloupec() > start.getSloupec() else -1
            vez_x = plocha.rozmery[0] if smer > 0 else 1
            plocha.setFigurku(plocha.delFigurku(start), cil)
            vez = plocha.setFigurku(plocha.delFigurku(Pol(vez_x, start.getRad())),
                                    Pol(start.getSloupec() + smer, start.getRad()))
            isrosada = True
            # postcheckmove není potřeba – král ani jedno pole nebylo ohrožené
        else:
            return False

        if not isrosada and not self.postcheckmove():
            # Vrácení tahu a vzkříšení vyhozené figurky
            plocha.setFigurku(plocha.vrat_obsah(cil), start)
            if not isenpassant:
                plocha.setFigurku(deadfig, cil)
            else:
                plocha.setFigurku(None, cil)
                plocha.setFigurku(deadfig, predTah.getCil())
            return False

        if self.tah.getNahradu():
            plocha.setFigurku(self.tah.getNahradu(), cil)
        plocha.setPredTah(self.tah)

        if not oznac:
            return True

        fig = self.tah.getFigurku()
        fig.setMoved()
        if vez is not None:
            vez.setMoved()
        if isrosada:
            self.tah.rosada = 1 if cil.getSloupec() > start.getSloupec() else 2
        if isenpassant:
            self.tah.enPassant = True
        if deadfig is not None:
            self.tah.capture = deadfig
            plocha.addVyhozenouFigurku(deadfig)
        self.tah.sach = self.check_sach()
        self.tah.mat = self.tah.sach and self.check_mat()
        self.tah.pat = (not self.tah.sach) and self.check_pat()
        return True

    def check_sach(self) -> bool:
        # True, pokud je soupeřův král po tomto tahu v šachu.
        fig = self.tah.getFigurku()
        return fig is not None and self.herni_plocha.check_sach(-fig.getBarvu()) != 0

    def check_mat(self) -> bool:
        fig = self.tah.getFigurku()
        return fig is not None and self.herni_plocha.check_mat(-fig.getBarvu())

    def check_pat(self) -> bool:
        fig = self.tah.getFigurku()
        return fig is not None and self.herni_plocha.check_pat(-fig.getBarvu())
