"""
Kwesty = úkoly (achievementy), které hráč plní během partie.

Kwest je definovaný daty, takže si uživatel může v editoru vytvořit vlastní:
  typ    – co se počítá (viz TYPY_KWESTU)
  pocet  – kolikrát se to musí stát (u 'rychla_vyhra' = max. počet vlastních tahů)
  kym    – filtr: značka figurky, kterou hráč táhne/bere/dává šach (None = libovolná)
  koho   – filtr: značka vyhozené figurky, nebo figurky, ve kterou se pěšec mění
  body   – odměna za splnění
"""

TYPY_KWESTU = {
    "tah":          "Proveď tahy",
    "vyhozeni":     "Vyhoď figurky",
    "sach":         "Dej šach",
    "mat":          "Dej mat",
    "rosada":       "Proveď rošádu",
    "en_passant":   "Vyhoď mimochodem",
    "promena":      "Proměň pěšce",
    "vyhra":        "Vyhraj partii",
    "rychla_vyhra": "Vyhraj do N tahů",
}


class Kwest:
    def __init__(self, nazev: str, popis: str, typ: str = "tah", pocet: int = 1,
                 kym: str | None = None, koho: str | None = None, body: int = 10, id: str | None = None):
        self.nazev = nazev
        self.popis = popis
        self.typ = typ
        self.pocet = max(1, int(pocet))
        self.kym = (kym or None) and kym.upper()
        self.koho = (koho or None) and koho.upper()
        self.body = int(body)
        self.id = id or self.vytvor_id(nazev)

    @staticmethod
    def vytvor_id(nazev: str) -> str:
        tabulka = str.maketrans("áčďéěíňóřšťúůýž", "acdeeinorstuuyz")
        s = nazev.lower().translate(tabulka)
        return "".join(c if c.isalnum() else "_" for c in s).strip("_") or "kwest"

    def validate(self) -> bool:
        return bool(self.nazev and self.popis and self.typ in TYPY_KWESTU and self.pocet >= 1)

    def je_na_konci_hry(self) -> bool:
        return self.typ in ("vyhra", "rychla_vyhra")

    def zapocitej(self, udalost: dict) -> int:
        """Kolik bodů postupu přinese tah popsaný událostí (0 nebo 1)."""
        kym_ok = self.kym is None or udalost.get("kym") == self.kym
        if self.typ == "tah":
            return int(kym_ok)
        if self.typ == "vyhozeni":
            koho = udalost.get("koho")
            return int(kym_ok and koho is not None and (self.koho is None or koho == self.koho))
        if self.typ == "sach":
            return int(kym_ok and bool(udalost.get("sach")))
        if self.typ == "mat":
            return int(kym_ok and bool(udalost.get("mat")))
        if self.typ == "rosada":
            return int(bool(udalost.get("rosada")))
        if self.typ == "en_passant":
            return int(bool(udalost.get("en_passant")))
        if self.typ == "promena":
            na = udalost.get("promena")
            return int(na is not None and (self.koho is None or na == self.koho))
        return 0

    def to_dict(self) -> dict:
        return {"id": self.id, "nazev": self.nazev, "popis": self.popis, "typ": self.typ,
                "pocet": self.pocet, "kym": self.kym, "koho": self.koho, "body": self.body}

    @staticmethod
    def from_dict(d: dict) -> "Kwest":
        return Kwest(d["nazev"], d.get("popis", ""), d.get("typ", "tah"), d.get("pocet", 1),
                     d.get("kym"), d.get("koho"), d.get("body", 10), d.get("id"))

    def __str__(self):
        return f"Kwest: {self.nazev}"
