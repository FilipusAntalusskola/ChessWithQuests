import json
from pathlib import Path

from model.uzivatel import Uzivatel


class UserManager:
    # Správa uživatelů: načtení/uložení, statistiky, ELO.

    K_FAKTOR = 32

    def __init__(self, soubor: str | Path | None = None):
        self.soubor = Path(soubor) if soubor else None
        self.uzivatele: dict[str, Uzivatel] = {}
        self.nacti()

    def nacti(self):
        if not self.soubor or not self.soubor.exists():
            return
        try:
            with open(self.soubor, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return
        for d in data.get("uzivatele", []):
            u = Uzivatel.from_dict(d)
            self.uzivatele[u.uzivatelske_jmeno] = u

    def uloz(self):
        if not self.soubor:
            return
        self.soubor.parent.mkdir(parents=True, exist_ok=True)
        with open(self.soubor, "w", encoding="utf-8") as f:
            json.dump({"uzivatele": [u.to_dict() for u in self.uzivatele.values()]}, f, ensure_ascii=False, indent=2)

    def jmena(self) -> list[str]:
        return sorted(self.uzivatele, key=str.lower)

    def najdi(self, jmeno: str) -> Uzivatel | None:
        return self.uzivatele.get(jmeno)

    def ziskej(self, jmeno: str) -> Uzivatel:
        # Najde uživatele, případně založí nového
        jmeno = jmeno.strip()
        if jmeno not in self.uzivatele:
            self.uzivatele[jmeno] = Uzivatel(jmeno)
        return self.uzivatele[jmeno]

    def smaz(self, jmeno: str):
        self.uzivatele.pop(jmeno, None)

    def zapis_vysledek(self, bily: Uzivatel, cerny: Uzivatel, skore_bileho: float) -> tuple[int, int]:
        """Zapíše výsledek partie (1 = bílý vyhrál, 0.5 = remíza, 0 = černý vyhrál),
        upraví ELO a vrátí změny ELO (bílý, černý)."""
        ocekavane = 1 / (1 + 10 ** ((cerny.elo - bily.elo) / 400))
        delta = round(self.K_FAKTOR * (skore_bileho - ocekavane))
        bily.incEloRating(delta)
        cerny.incEloRating(-delta)
        for u in (bily, cerny):
            u.partie += 1
        if skore_bileho == 1:
            bily.vyhry += 1
            cerny.prohry += 1
        elif skore_bileho == 0:
            cerny.vyhry += 1
            bily.prohry += 1
        else:
            bily.remizy += 1
            cerny.remizy += 1
        return delta, -delta
