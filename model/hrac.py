from model.uzivatel import Uzivatel


class Hrac:
    # Hráč v jedné partii: barva + uživatel

    def __init__(self, barva: int, uzivatel: Uzivatel):
        self.barva = barva          # 1 = bílý, -1 = černý
        self.uzivatel = uzivatel

    def __str__(self):
        return f"{self.uzivatel.uzivatelske_jmeno} ({self.nazev_barvy()})"

    def nazev_barvy(self) -> str:
        return "Bílý" if self.barva == 1 else "Černý"

    def getBarvu(self) -> int:
        return self.barva

    def getJmeno(self) -> str:
        return self.uzivatel.uzivatelske_jmeno

    def getEloRating(self) -> int:
        return self.uzivatel.getEloRating()
