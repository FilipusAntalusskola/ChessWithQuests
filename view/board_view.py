import tkinter as tk

from model.pol import Pol
from view import theme
from view.theme import B


class BoardView(tk.Canvas):
    """Šachovnice libovolné velikosti. Sama nic nerozhoduje – jen kreslí a hlásí kliknutí."""

    def __init__(self, master, pri_kliknuti):
        super().__init__(master, bg=B["pozadi"], highlightthickness=0)
        self.pri_kliknuti = pri_kliknuti
        self.plocha = None
        self.otoceno = False
        self.vyber: Pol | None = None
        self.cile: set[Pol] = set()
        self.brani: set[Pol] = set()
        self.posledni: tuple[Pol, Pol] | None = None
        self.sach: Pol | None = None
        self._geom = (0, 0, 40)        # x0, y0, velikost pole
        self.bind("<Configure>", lambda e: self.prekresli())
        self.bind("<Button-1>", self._klik)

    def nastav(self, plocha, otoceno=False, vyber=None, cile=(), brani=(), posledni=None, sach=None):
        self.plocha = plocha
        self.otoceno = otoceno
        self.vyber = vyber
        self.cile = set(cile)
        self.brani = set(brani)
        self.posledni = posledni
        self.sach = sach
        self.prekresli()

    # --- převod souřadnic ---
    def _pol_na_xy(self, pol: Pol) -> tuple[float, float]:
        x0, y0, s = self._geom
        sirka, vyska = self.plocha.rozmery
        if self.otoceno:
            sl, rd = sirka - pol.getSloupec(), pol.getRad() - 1
        else:
            sl, rd = pol.getSloupec() - 1, vyska - pol.getRad()
        return x0 + sl * s, y0 + rd * s

    def _xy_na_pol(self, x: float, y: float) -> Pol | None:
        x0, y0, s = self._geom
        sirka, vyska = self.plocha.rozmery
        sl, rd = int((x - x0) // s), int((y - y0) // s)
        if not (0 <= sl < sirka and 0 <= rd < vyska):
            return None
        if self.otoceno:
            return Pol(sirka - sl, rd + 1)
        return Pol(sl + 1, vyska - rd)

    def _klik(self, event):
        if self.plocha is None:
            return
        pol = self._xy_na_pol(event.x, event.y)
        if pol is not None:
            self.pri_kliknuti(pol)

    # --- kreslení ---
    def prekresli(self):
        self.delete("all")
        if self.plocha is None:
            return
        w, h = max(self.winfo_width(), 100), max(self.winfo_height(), 100)
        sirka, vyska = self.plocha.rozmery
        okraj_txt = 22
        s = max(16, int(min((w - okraj_txt - 16) / sirka, (h - okraj_txt - 16) / vyska)))
        x0 = (w - s * sirka + okraj_txt) / 2
        y0 = (h - s * vyska - okraj_txt) / 2
        self._geom = (x0, y0, s)

        # rám
        self.create_rectangle(x0 - 6, y0 - 6, x0 + s * sirka + 6, y0 + s * vyska + 6,
                              fill=B["okraj"], outline=B["akcent_tmavy"], width=2)

        posl = set(self.posledni) if self.posledni else set()
        for sl in range(1, sirka + 1):
            for rd in range(1, vyska + 1):
                pol = Pol(sl, rd)
                x, y = self._pol_na_xy(pol)
                svetle = (sl + rd) % 2 == 1
                barva = B["svetle_pole"] if svetle else B["tmave_pole"]
                if pol in posl:
                    barva = B["posledni_svetle"] if svetle else B["posledni_tmave"]
                self.create_rectangle(x, y, x + s, y + s, fill=barva, outline="")
                if pol == self.sach:
                    for i, t in enumerate((0.15, 0.3, 0.45)):
                        o = s * (0.05 + i * 0.08)
                        self.create_oval(x + o, y + o, x + s - o, y + s - o, outline="",
                                         fill=theme.smichej(barva, B["sach"], 0.35 + t))
                if pol == self.vyber:
                    self.create_rectangle(x + 2, y + 2, x + s - 2, y + s - 2, outline=B["vyber"], width=4)

        # popisky sloupců a řad
        f = ("Georgia", max(8, min(12, int(s * 0.22))))
        for sl in range(1, sirka + 1):
            x, _ = self._pol_na_xy(Pol(sl, 1 if not self.otoceno else vyska))
            self.create_text(x + s / 2, y0 + s * vyska + 15, text=chr(96 + sl), fill=B["tlumeny"], font=f)
        for rd in range(1, vyska + 1):
            _, y = self._pol_na_xy(Pol(1 if not self.otoceno else sirka, rd))
            self.create_text(x0 - 16, y + s / 2, text=str(rd), fill=B["tlumeny"], font=f)

        # figurky
        for pol, fig in self.plocha.figurky():
            x, y = self._pol_na_xy(pol)
            theme.nakresli_figurku(self, fig, x + s / 2, y + s / 2, s)

        # možné tahy
        for pol in self.cile:
            x, y = self._pol_na_xy(pol)
            if pol in self.brani:
                self.create_oval(x + s * 0.06, y + s * 0.06, x + s * 0.94, y + s * 0.94,
                                 outline=B["tecka"], width=max(3, int(s * 0.08)))
            else:
                r = s * 0.15
                self.create_oval(x + s / 2 - r, y + s / 2 - r, x + s / 2 + r, y + s / 2 + r,
                                 fill=B["tecka"], outline="")
