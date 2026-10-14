import copy


class Pol:
    """Jedno pole šachovnice, dané souřadnicemi (sloupec, řada), obojí od 1."""

    def __init__(self, sloupec: int, rad: int):
        self.sloupec = sloupec
        self.rad = rad

    def __str__(self) -> str:
        # Sloupce a..p (max. 16), řady jako číslo (funguje i pro 10 a víc)
        return chr(self.sloupec + 96) + str(self.rad)

    def __repr__(self) -> str:
        return f"Pol({self.sloupec},{self.rad})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pol):
            return False
        return self.sloupec == other.sloupec and self.rad == other.rad

    def __hash__(self) -> int:
        return hash((self.sloupec, self.rad))

    def copy(self):
        return copy.copy(self)

    def getSloupec(self) -> int:
        return self.sloupec

    def getRad(self) -> int:
        return self.rad


if __name__ == '__main__':
    p = Pol(3, 4)
    print(p, p.getSloupec(), p.getRad())
