"""
Definovatelné figurky.

Definice figurky se ukládá do data/figurky.json. Pohyb se zapisuje textem,
jeden řádek = jedna skupina vektorů se stejným dosahem:

    vektory ; dosah ; vpřed

  vektory  – mezerou oddělené dvojice dx,dy (z pohledu bílého, dy>0 = dopředu)
  dosah    – kolikrát se smí vektor zopakovat, 0 = neomezeně (výchozí 0)
  vpřed    – nepovinné slovo; figurka pak jde jen ve směru vektoru (jako pěšec),
             jinak jde i opačným směrem

Příklad – Arcibiskup (střelec + jezdec):
    1,1 1,-1
    1,2 1,-2 2,1 2,-1 ; 1
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from model.figurka import Figurka, DefinovanaFigurka, VESTAVENE_TRIDY

NEOMEZENY_DOSAH_VPRED = 99   # "neomezeně" u figurek jdoucích jen vpřed


@dataclass
class Pohyb:
    vektory: list[tuple[int, int]]
    dosah: int = 0          # 0 = neomezeně
    vpred: bool = False     # True = jen dopředu (z pohledu hráče)

    def to_dict(self):
        return {"vektory": [list(v) for v in self.vektory], "dosah": self.dosah, "vpred": self.vpred}

    @staticmethod
    def from_dict(d) -> "Pohyb":
        return Pohyb([tuple(v) for v in d["vektory"]], int(d.get("dosah", 0)), bool(d.get("vpred", False)))


@dataclass
class DefiniceFigurky:
    znacka: str
    nazev: str
    pohyby: list[Pohyb]
    utoky: list[Pohyb] = field(default_factory=list)   # prázdné = útočí stejně jako se pohybuje
    skok: bool = False
    symbol: str = ""
    popis: str = ""
    vestavena: bool = False

    # --- převod na vektory/rozsahy pro třídu Figurka ---
    @staticmethod
    def rozbal(pohyby: list[Pohyb], barva: int):
        vektory, rozsahy = [], []
        for p in pohyby:
            if p.vpred:
                n = p.dosah if p.dosah > 0 else NEOMEZENY_DOSAH_VPRED
                rozsah = {barva, n * barva}
            else:
                rozsah = None if p.dosah == 0 else {-p.dosah, p.dosah}
            for v in p.vektory:
                vektory.append(tuple(v))
                rozsahy.append(rozsah)
        return vektory, rozsahy

    def to_dict(self):
        return {
            "znacka": self.znacka, "nazev": self.nazev,
            "pohyby": [p.to_dict() for p in self.pohyby],
            "utoky": [p.to_dict() for p in self.utoky],
            "skok": self.skok, "symbol": self.symbol, "popis": self.popis,
        }

    @staticmethod
    def from_dict(d) -> "DefiniceFigurky":
        return DefiniceFigurky(
            znacka=d["znacka"].upper(), nazev=d["nazev"],
            pohyby=[Pohyb.from_dict(p) for p in d.get("pohyby", [])],
            utoky=[Pohyb.from_dict(p) for p in d.get("utoky", [])],
            skok=bool(d.get("skok", False)), symbol=d.get("symbol", ""), popis=d.get("popis", ""),
        )


# ---------------------------------------------------------------- text <-> pohyby

def parse_pohyby(text: str) -> list[Pohyb]:
    """Převede text z editoru na seznam pohybů. Při chybě vyhodí ValueError s českou zprávou."""
    pohyby = []
    for cislo, radek in enumerate(text.splitlines(), start=1):
        radek = radek.strip()
        if not radek or radek.startswith('#'):
            continue
        casti = [c.strip() for c in radek.split(';')]
        vektory = []
        for token in casti[0].split():
            try:
                dx, dy = (int(x) for x in token.split(','))
            except ValueError:
                raise ValueError(f"Řádek {cislo}: '{token}' není vektor ve tvaru dx,dy (např. 1,2).")
            if dx == 0 and dy == 0:
                raise ValueError(f"Řádek {cislo}: vektor 0,0 nemá smysl.")
            if abs(dx) > 15 or abs(dy) > 15:
                raise ValueError(f"Řádek {cislo}: vektor {token} je příliš dlouhý.")
            vektory.append((dx, dy))
        if not vektory:
            raise ValueError(f"Řádek {cislo}: chybí vektory.")
        dosah, vpred = 0, False
        for c in casti[1:]:
            if not c:
                continue
            if c.lower() in ("vpřed", "vpred", "v"):
                vpred = True
            else:
                try:
                    dosah = int(c)
                except ValueError:
                    raise ValueError(f"Řádek {cislo}: '{c}' – čekám číslo (dosah) nebo slovo 'vpřed'.")
                if dosah < 0:
                    raise ValueError(f"Řádek {cislo}: dosah nesmí být záporný.")
        pohyby.append(Pohyb(vektory, dosah, vpred))
    return pohyby


def format_pohyby(pohyby: list[Pohyb]) -> str:
    radky = []
    for p in pohyby:
        s = " ".join(f"{dx},{dy}" for dx, dy in p.vektory)
        if p.dosah or p.vpred:
            s += f" ; {p.dosah}"
        if p.vpred:
            s += " ; vpřed"
        radky.append(s)
    return "\n".join(radky)


# ---------------------------------------------------------------- vestavěné figurky

def _vestavene() -> list[DefiniceFigurky]:
    osm = [(0, 1), (1, 1), (1, 0), (1, -1)]
    return [
        DefiniceFigurky('K', 'Král', [Pohyb(osm, 1)], popis="O jedno pole libovolným směrem. Umí rošádu.", vestavena=True),
        DefiniceFigurky('D', 'Dáma', [Pohyb(osm, 0)], popis="Libovolně daleko rovně i šikmo.", vestavena=True),
        DefiniceFigurky('V', 'Věž', [Pohyb([(0, 1), (1, 0)], 0)], popis="Libovolně daleko rovně.", vestavena=True),
        DefiniceFigurky('S', 'Střelec', [Pohyb([(1, 1), (1, -1)], 0)], popis="Libovolně daleko šikmo.", vestavena=True),
        DefiniceFigurky('J', 'Jezdec', [Pohyb([(1, 2), (1, -2), (2, 1), (2, -1)], 1)], skok=True,
                        popis="Skok do L, přeskakuje figurky.", vestavena=True),
        DefiniceFigurky('P', 'Pěšec', [Pohyb([(0, 1)], 2, True)], [Pohyb([(1, 1), (-1, 1)], 1, True)],
                        popis="Vpřed o 1 (z výchozí pozice o 2), bere šikmo. En passant, proměna.", vestavena=True),
    ]


class RegistrFigurek:
    """Seznam všech známých figurek (vestavěné + vlastní ze souboru)."""

    def __init__(self, soubor: str | Path | None = None):
        self.soubor = Path(soubor) if soubor else None
        self.definice: dict[str, DefiniceFigurky] = {d.znacka: d for d in _vestavene()}
        if self.soubor:
            self.nacti()

    def nacti(self):
        if not self.soubor or not self.soubor.exists():
            return
        with open(self.soubor, encoding="utf-8") as f:
            data = json.load(f)
        for d in data.get("figurky", []):
            try:
                definice = DefiniceFigurky.from_dict(d)
            except (KeyError, ValueError, TypeError):
                continue    # poškozený záznam přeskočíme
            if definice.znacka not in VESTAVENE_TRIDY:
                self.definice[definice.znacka] = definice

    def uloz(self):
        if not self.soubor:
            return
        self.soubor.parent.mkdir(parents=True, exist_ok=True)
        vlastni = [d.to_dict() for d in self.definice.values() if not d.vestavena]
        with open(self.soubor, "w", encoding="utf-8") as f:
            json.dump({"figurky": vlastni}, f, ensure_ascii=False, indent=2)

    def seznam(self) -> list[DefiniceFigurky]:
        return list(self.definice.values())

    def znacky(self) -> list[str]:
        return list(self.definice.keys())

    def get(self, znacka: str) -> DefiniceFigurky | None:
        return self.definice.get(znacka.upper())

    def pridej(self, definice: DefiniceFigurky):
        if definice.znacka in VESTAVENE_TRIDY:
            raise ValueError(f"Značka {definice.znacka} patří vestavěné figurce.")
        if len(definice.znacka) != 1 or not definice.znacka.isalpha():
            raise ValueError("Značka musí být jedno písmeno.")
        if not definice.nazev.strip():
            raise ValueError("Figurka musí mít název.")
        if not definice.pohyby:
            raise ValueError("Figurka musí mít aspoň jeden pohyb.")
        self.definice[definice.znacka] = definice

    def odeber(self, znacka: str):
        d = self.definice.get(znacka)
        if d is None or d.vestavena:
            raise ValueError("Vestavěnou figurku nelze smazat.")
        del self.definice[znacka]

    def vytvor(self, znacka: str, barva: int) -> Figurka:
        znacka = znacka.upper()
        if znacka in VESTAVENE_TRIDY:
            return VESTAVENE_TRIDY[znacka](barva)
        d = self.definice.get(znacka)
        if d is None:
            raise KeyError(f"Neznámá figurka '{znacka}'.")
        return DefinovanaFigurka(d, barva)

    def figurky_pro_promenu(self) -> list[str]:
        # Pěšec se může proměnit ve všechno kromě krále a pěšce
        return [z for z in self.definice if z not in ('K', 'P')]
