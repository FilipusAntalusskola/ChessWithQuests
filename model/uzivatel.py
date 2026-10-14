class Uzivatel:
    # Osoba, která hraje (nebo hrála) partie. Ukládá se do data/uzivatele.json.

    def __init__(self, uzivatelske_jmeno: str, jmeno: str = "", email: str = "", elo: int = 1200):
        self.uzivatelske_jmeno = uzivatelske_jmeno
        self.jmeno = jmeno or uzivatelske_jmeno
        self.email = email
        self.elo = elo
        self.splnene_kvesty: list[str] = []     # id splněných kwestů
        self.body = 0                           # body za kwesty
        self.partie = 0
        self.vyhry = 0
        self.remizy = 0
        self.prohry = 0

    def __str__(self):
        n = len(self.splnene_kvesty)
        if n == 1:
            s = "1 splněný kwest"
        elif 1 < n < 5:
            s = f"{n} splněné kwesty"
        else:
            s = f"{n} splněných kwestů"
        return f"{self.uzivatelske_jmeno} (ELO {self.elo}, {s})"

    def getUzivatelskeJmeno(self) -> str:
        return self.uzivatelske_jmeno

    def getJmeno(self) -> str:
        return self.jmeno

    def setJmeno(self, jmeno: str):
        self.jmeno = jmeno
        return self

    def getEmail(self) -> str:
        return self.email

    def setEmail(self, email: str):
        self.email = email
        return self

    def getEloRating(self) -> int:
        return self.elo

    def setEloRating(self, elo: int) -> int:
        self.elo = elo
        return self.elo

    def incEloRating(self, delta_elo: int) -> int:
        self.elo += delta_elo
        return self.elo

    def getSplneneKwesty(self) -> list[str]:
        return self.splnene_kvesty

    def ma_kwest(self, kwest_id: str) -> bool:
        return kwest_id in self.splnene_kvesty

    def pridej_kwest(self, kwest, body: int = 0):
        # Přijme objekt Kwest nebo rovnou jeho id
        kid = getattr(kwest, "id", kwest)
        if kid not in self.splnene_kvesty:
            self.splnene_kvesty.append(kid)
            self.body += body if body else getattr(kwest, "body", 0)
        return self

    def to_dict(self) -> dict:
        return {
            "uzivatelske_jmeno": self.uzivatelske_jmeno, "jmeno": self.jmeno, "email": self.email,
            "elo": self.elo, "splnene_kvesty": self.splnene_kvesty, "body": self.body,
            "partie": self.partie, "vyhry": self.vyhry, "remizy": self.remizy, "prohry": self.prohry,
        }

    @staticmethod
    def from_dict(d: dict) -> "Uzivatel":
        u = Uzivatel(d["uzivatelske_jmeno"], d.get("jmeno", ""), d.get("email", ""), int(d.get("elo", 1200)))
        u.splnene_kvesty = list(d.get("splnene_kvesty", []))
        for klic in ("body", "partie", "vyhry", "remizy", "prohry"):
            setattr(u, klic, int(d.get(klic, 0)))
        return u
