"""
Figurky.

Barvy:  1 = bílý,  -1 = černý.

Pohyb figurky je popsán seznamem základních vektorů (dx, dy) a rozsahem násobků,
kterými se dá vektor vynásobit. Např. věž má vektory (0,1) a (1,0) a rozsah
{-7, 7}, takže dojede kamkoli v řadě či sloupci. Jezdec má rozsah {-1, 1}.
Rozsah None znamená "neomezeně" (až k okraji desky).

Každý vektor může mít vlastní rozsah (seznam `rozsahy`). Díky tomu jde
nadefinovat i kombinovanou figurku, např. střelec + jezdec.
Vektory se zadávají z pohledu bílého; u černého se "dopředu" otočí samo,
protože rozsah je {barva, n*barva}.
"""
import copy
from model.pol import Pol


class Figurka:
    # Základní třída všech figurek

    def __init__(self, nazev: str,
                 barva: int,
                 vektory: list[tuple[int, int]],
                 vektory_utoku: list[tuple[int, int]] | None = None,
                 moveRange: set[int] | None = None,
                 skok: bool = False,
                 znacka: str | None = None,
                 symbol: str = "",
                 rozsahy: list[set[int] | None] | None = None,
                 rozsahy_utoku: list[set[int] | None] | None = None):
        self.nazev = nazev
        self.barva = barva                      # 1 = bílý; -1 = černý
        self.znacka = (znacka or nazev[0]).upper()
        self.symbol = symbol                    # volitelný znak pro GUI (vlastní figurky)
        self.vektory = [tuple(v) for v in vektory]
        self.vektory_utoku = [tuple(v) for v in vektory_utoku] if vektory_utoku is not None else list(self.vektory)
        self.moveRange = None if moveRange is None else set(moveRange)
        self.skok = skok                        # True = přeskakuje figurky (cesta se nekontroluje)

        if rozsahy is None:
            rozsahy = [self.moveRange] * len(self.vektory)
        self.rozsahy = [None if r is None else set(r) for r in rozsahy]
        if rozsahy_utoku is None:
            rozsahy_utoku = list(self.rozsahy) if vektory_utoku is None else [self.moveRange] * len(self.vektory_utoku)
        self.rozsahy_utoku = [None if r is None else set(r) for r in rozsahy_utoku]

        self._normVektory = self._vektornormer(self.vektory)
        self._normVektoryUtoku = self._vektornormer(self.vektory_utoku)
        self._moved = False

    def __str__(self):
        return self.znacka

    def __repr__(self):
        return f"{self.nazev}({'b' if self.barva == 1 else 'č'})"

    def copy(self):
        return copy.deepcopy(self)

    # --- přístupové metody (z původního projektu) ---
    def getVektory(self) -> list[tuple[int, int]]:
        return self.vektory

    def getVektoryUtoku(self) -> list[tuple[int, int]]:
        return self.vektory_utoku

    def getNormVektory(self) -> list[tuple[int, int]]:
        return self._normVektory

    def getNormVektoryUtoku(self) -> list[tuple[int, int]]:
        return self._normVektoryUtoku

    def getBarvu(self) -> int:
        return self.barva

    def getNazev(self) -> str:
        return self.nazev

    def getZnacku(self) -> str:
        return self.znacka

    def getMoveRange(self) -> set[int] | None:
        return self.moveRange

    def getMoveRangeUtoku(self) -> set[int] | None:
        return self.moveRange

    def getRozsah(self, index: int, utok: bool) -> set[int] | None:
        # Rozsah násobků pro konkrétní vektor
        return self.rozsahy_utoku[index] if utok else self.rozsahy[index]

    def setMoved(self):
        self._moved = True

    def isMoved(self) -> bool:
        return self._moved

    def getAllReachable(self, pozice: Pol, rozmery: tuple[int, int]) -> set[Pol]:
        # Vrátí všechna pole, kam by figurka teoreticky mohla dojet (bez ohledu na ostatní figurky).
        # Je to jen "první odhad" – skutečnou platnost kontroluje RevizorTahu.
        targets = set()
        for utok, vektory in ((False, self.vektory), (True, self.vektory_utoku)):
            for i, vekt in enumerate(vektory):
                rozsah = self.getRozsah(i, utok)
                if rozsah is None:
                    m = max(rozmery)
                    rozsah = {-m, m}
                for rg in (min(rozsah), max(rozsah)):
                    if rg == 0:
                        continue
                    smer = 1 if rg > 0 else -1
                    # Pokud rozsah nezačíná u 1 (např. {2,3}), začneme od nejmenšího násobku
                    od = 1
                    if min(rozsah) > 0 or max(rozsah) < 0:
                        od = min(abs(min(rozsah)), abs(max(rozsah)))
                    for k in range(od, abs(rg) + 1):
                        x = pozice.getSloupec() + smer * k * vekt[0]
                        y = pozice.getRad() + smer * k * vekt[1]
                        if x < 1 or x > rozmery[0] or y < 1 or y > rozmery[1]:
                            break
                        targets.add(Pol(x, y))
        return targets

    @staticmethod
    def _vektornormer(vektory: list[tuple[int, int]]) -> list[tuple[int, int]]:
        # Normálové vektory (otočené o 90°) – slouží ke zjištění kolinearity skalárním součinem
        return [(-y, x) for (x, y) in vektory]


class Kral(Figurka):
    def __init__(self, barva):
        vektory = [(0, 1), (1, 1), (1, 0), (1, -1)]
        super().__init__('Král', barva, vektory, moveRange={-1, 1}, znacka='K')


class Dama(Figurka):
    def __init__(self, barva):
        vektory = [(0, 1), (1, 1), (1, 0), (1, -1)]
        super().__init__('Dáma', barva, vektory, znacka='D')


class Strelec(Figurka):
    def __init__(self, barva):
        vektory = [(1, 1), (1, -1)]
        super().__init__('Střelec', barva, vektory, znacka='S')


class Kun(Figurka):
    def __init__(self, barva):
        vektory = [(1, 2), (1, -2), (2, 1), (2, -1)]
        super().__init__('Jezdec', barva, vektory, moveRange={-1, 1}, skok=True, znacka='J')


class Vez(Figurka):
    def __init__(self, barva):
        vektory = [(0, 1), (1, 0)]
        super().__init__('Věž', barva, vektory, znacka='V')


class Pesak(Figurka):
    def __init__(self, barva):
        vektory = [(0, 1)]
        vektory_utoku = [(1, 1), (-1, 1)]
        super().__init__('Pěšec', barva, vektory, vektory_utoku, moveRange={barva, 2 * barva}, znacka='P')

    def setMoved(self):
        super().setMoved()
        self.moveRange = {self.barva}

    def getMoveRangeUtoku(self):
        return {self.barva}

    def getRozsah(self, index: int, utok: bool) -> set[int] | None:
        return {self.barva} if utok else self.moveRange


class DefinovanaFigurka(Figurka):
    """Figurka vytvořená podle uživatelské definice (viz model/definice_figurek.py)."""

    def __init__(self, definice, barva: int):
        vektory, rozsahy = definice.rozbal(definice.pohyby, barva)
        if definice.utoky:
            vektory_utoku, rozsahy_utoku = definice.rozbal(definice.utoky, barva)
        else:
            vektory_utoku, rozsahy_utoku = None, None
        super().__init__(definice.nazev, barva, vektory, vektory_utoku,
                         skok=definice.skok, znacka=definice.znacka, symbol=definice.symbol,
                         rozsahy=rozsahy, rozsahy_utoku=rozsahy_utoku)


VESTAVENE_TRIDY = {'K': Kral, 'D': Dama, 'V': Vez, 'S': Strelec, 'J': Kun, 'P': Pesak}


if __name__ == "__main__":
    f = Pesak(1)
    print(f, f.getVektory(), f.getAllReachable(Pol(2, 2), (8, 8)))
