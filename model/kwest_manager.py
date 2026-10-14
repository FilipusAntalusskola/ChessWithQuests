import copy
import json
from pathlib import Path

from model.kwest import Kwest


class KwestKatalog:
    """Seznam všech definovaných kwestů (data/kwesty.json)."""

    def __init__(self, soubor: str | Path | None = None):
        self.soubor = Path(soubor) if soubor else None
        self.kwesty: list[Kwest] = []
        self.nacti()

    def nacti(self):
        self.kwesty = []
        if not self.soubor or not self.soubor.exists():
            return
        with open(self.soubor, encoding="utf-8") as f:
            data = json.load(f)
        for d in data.get("kwesty", []):
            try:
                k = Kwest.from_dict(d)
            except (KeyError, ValueError, TypeError):
                continue
            if k.validate():
                self.kwesty.append(k)

    def uloz(self):
        if not self.soubor:
            return
        self.soubor.parent.mkdir(parents=True, exist_ok=True)
        with open(self.soubor, "w", encoding="utf-8") as f:
            json.dump({"kwesty": [k.to_dict() for k in self.kwesty]}, f, ensure_ascii=False, indent=2)

    def najdi(self, kid: str) -> Kwest | None:
        return next((k for k in self.kwesty if k.id == kid), None)

    def pridej(self, kwest: Kwest):
        if not kwest.validate():
            raise ValueError("Kwest musí mít název, popis, typ a počet ≥ 1.")
        stary = self.najdi(kwest.id)
        if stary is not None:
            self.kwesty[self.kwesty.index(stary)] = kwest
        else:
            self.kwesty.append(kwest)

    def odeber(self, kid: str):
        self.kwesty = [k for k in self.kwesty if k.id != kid]


class KwestManager:
    """Sleduje plnění kwestů v jedné partii pro oba hráče (index 0 = bílý, 1 = černý)."""

    def __init__(self, kwesty: list[Kwest] | None = None, splnene_drive: list[set[str]] | None = None):
        self.kvesty: list[Kwest] = list(kwesty or [])
        self.splnene_drive = splnene_drive or [set(), set()]   # z předchozích partií
        self.postup: list[dict[str, int]] = [{}, {}]
        self.splnene_ted: list[list[str]] = [[], []]

    def pridej_kwest(self, kwest: Kwest):
        self.kvesty.append(kwest)

    def method(self, typ):
        # z verze (4): najde první kwest daného typu
        return next((k for k in self.kvesty if k.typ == typ), None)

    def je_splneny(self, hrac: int, kwest: Kwest) -> bool:
        return kwest.id in self.splnene_drive[hrac] or kwest.id in self.splnene_ted[hrac]

    def stav(self, hrac: int, kwest: Kwest) -> tuple[int, str]:
        """(postup, stav) kde stav je 'drive', 'ted' nebo ''."""
        if kwest.id in self.splnene_drive[hrac]:
            return kwest.pocet, "drive"
        if kwest.id in self.splnene_ted[hrac]:
            return kwest.pocet, "ted"
        return self.postup[hrac].get(kwest.id, 0), ""

    def _splnit(self, hrac: int, kwest: Kwest) -> None:
        self.splnene_ted[hrac].append(kwest.id)

    def zpracuj_tah(self, hrac: int, udalost: dict) -> list[Kwest]:
        nove = []
        for k in self.kvesty:
            if k.je_na_konci_hry() or self.je_splneny(hrac, k):
                continue
            prirustek = k.zapocitej(udalost)
            if prirustek:
                self.postup[hrac][k.id] = self.postup[hrac].get(k.id, 0) + prirustek
                if self.postup[hrac][k.id] >= k.pocet:
                    self._splnit(hrac, k)
                    nove.append(k)
        return nove

    def zpracuj_konec(self, vitez: int | None, pocet_tahu: list[int]) -> list[tuple[int, Kwest]]:
        nove = []
        if vitez is None:
            return nove
        for k in self.kvesty:
            if self.je_splneny(vitez, k):
                continue
            if k.typ == "vyhra" or (k.typ == "rychla_vyhra" and pocet_tahu[vitez] <= k.pocet):
                self._splnit(vitez, k)
                nove.append((vitez, k))
        return nove

    def body_ted(self, hrac: int) -> int:
        return sum(k.body for k in self.kvesty if k.id in self.splnene_ted[hrac])

    # --- pro "tah zpět" ---
    def uloz_stav(self):
        return copy.deepcopy((self.postup, self.splnene_ted))

    def obnov_stav(self, stav):
        self.postup, self.splnene_ted = copy.deepcopy(stav)
