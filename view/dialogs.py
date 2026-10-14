import tkinter as tk
from tkinter import ttk, messagebox

from model.herni_plocha import vychozi_rada, MIN_SIRKA, MAX_SIRKA, MIN_VYSKA, MAX_VYSKA
from view import theme
from view.theme import B


class Dialog(tk.Toplevel):
    """Modální okno; výsledek je v self.vysledek (None = zrušeno)."""

    def __init__(self, master, titulek: str):
        super().__init__(master)
        self.title(titulek)
        self.configure(bg=B["panel"])
        self.transient(master)
        self.resizable(False, False)
        self.vysledek = None
        self.protocol("WM_DELETE_WINDOW", self.zrus)
        self.bind("<Escape>", lambda e: self.zrus())

    def vycentruj(self):
        self.update_idletasks()
        m = self.master.winfo_toplevel()
        x = m.winfo_rootx() + (m.winfo_width() - self.winfo_width()) // 2
        y = m.winfo_rooty() + (m.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(0, x)}+{max(0, y)}")

    def ukaz(self):
        self.vycentruj()
        try:
            self.wait_visibility()      # na Linuxu jinak grab_set selže
            self.grab_set()
        except tk.TclError:
            pass
        self.focus_set()
        self.wait_window()
        return self.vysledek

    def zrus(self):
        self.vysledek = None
        self.destroy()


class PromenaDialog(Dialog):
    """Výběr figurky při proměně pěšce."""

    def __init__(self, master, registr, barva: int):
        super().__init__(master, "Proměna pěšce")
        theme.stitek(self, "Ve kterou figurku se pěšec promění?", theme.H2).pack(padx=16, pady=(14, 8))
        mrizka = tk.Frame(self, bg=B["panel"])
        mrizka.pack(padx=12, pady=(0, 14))
        for i, znacka in enumerate(registr.figurky_pro_promenu()):
            fig = registr.vytvor(znacka, barva)
            bunka = tk.Frame(mrizka, bg=B["panel2"], cursor="hand2")
            bunka.grid(row=i // 4, column=i % 4, padx=4, pady=4)
            c = tk.Canvas(bunka, width=64, height=64, bg=B["svetle_pole"], highlightthickness=0, cursor="hand2")
            c.pack(padx=4, pady=(4, 0))
            theme.nakresli_figurku(c, fig, 32, 32, 60)
            lbl = theme.stitek(bunka, fig.getNazev(), theme.MALY, bg=B["panel2"])
            lbl.pack(pady=(2, 4))
            for w in (bunka, c, lbl):
                w.bind("<Button-1>", lambda e, z=znacka: self._vyber(z))

    def _vyber(self, znacka):
        self.vysledek = znacka
        self.destroy()


class NovaHraDialog(Dialog):
    """Nastavení nové partie: hráči, velikost desky, rozestavení, čas."""

    def __init__(self, master, registr, znama_jmena: list[str], predchozi: dict | None = None):
        super().__init__(master, "Nová partie")
        self.registr = registr
        p = predchozi or {}
        obal = tk.Frame(self, bg=B["panel"])
        obal.pack(padx=20, pady=16)

        theme.stitek(obal, "Nová partie", theme.H2, fg=B["akcent"]).grid(row=0, column=0, columnspan=3,
                                                                          sticky="w", pady=(0, 10))
        r = 1
        self.bily = tk.StringVar(value=p.get("bily", "Hráč 1"))
        self.cerny = tk.StringVar(value=p.get("cerny", "Hráč 2"))
        for text, var in (("Bílý hráč:", self.bily), ("Černý hráč:", self.cerny)):
            theme.stitek(obal, text).grid(row=r, column=0, sticky="w", pady=3)
            cb = ttk.Combobox(obal, textvariable=var, values=znama_jmena, width=28)
            cb.grid(row=r, column=1, columnspan=2, sticky="ew", pady=3)
            r += 1

        ttk.Separator(obal).grid(row=r, column=0, columnspan=3, sticky="ew", pady=10)
        r += 1
        self.sirka = tk.IntVar(value=p.get("sirka", 8))
        self.vyska = tk.IntVar(value=p.get("vyska", 8))
        theme.stitek(obal, "Velikost desky:").grid(row=r, column=0, sticky="w")
        velikost = tk.Frame(obal, bg=B["panel"])
        velikost.grid(row=r, column=1, columnspan=2, sticky="w")
        ttk.Spinbox(velikost, from_=MIN_SIRKA, to=MAX_SIRKA, textvariable=self.sirka, width=4,
                    command=self._zmena_sirky).pack(side="left")
        theme.stitek(velikost, " sloupců  ×  ").pack(side="left")
        ttk.Spinbox(velikost, from_=MIN_VYSKA, to=MAX_VYSKA, textvariable=self.vyska, width=4).pack(side="left")
        theme.stitek(velikost, " řad").pack(side="left")
        r += 1

        theme.stitek(obal, "Základní řada:").grid(row=r, column=0, sticky="w", pady=(8, 3))
        self.rada = tk.StringVar(value=p.get("rada", vychozi_rada(self.sirka.get())))
        e = theme.vstup(obal, textvariable=self.rada, width=24)
        e.configure(font=("Consolas", 12, "bold"))
        e.grid(row=r, column=1, sticky="ew", pady=(8, 3))
        theme.tlacitko(obal, "Výchozí", self._vychozi).grid(row=r, column=2, padx=(6, 0), pady=(8, 3))
        r += 1
        legenda = "   ".join(f"{d.znacka} {d.nazev}" for d in registr.seznam())
        theme.stitek(obal, legenda + "   . prázdné pole", theme.MALY, fg=B["tlumeny"], wraplength=380,
                     justify="left").grid(row=r, column=1, columnspan=2, sticky="w")
        r += 1
        theme.stitek(obal, "Černý má řadu zrcadlově nahoře, král musí být právě jeden.", theme.MALY,
                     fg=B["tlumeny"]).grid(row=r, column=1, columnspan=2, sticky="w", pady=(0, 4))
        r += 1

        self.pesci = tk.BooleanVar(value=p.get("pesci", True))
        ttk.Checkbutton(obal, text="Řada pěšců před figurkami", variable=self.pesci).grid(
            row=r, column=1, columnspan=2, sticky="w", pady=2)
        r += 1

        ttk.Separator(obal).grid(row=r, column=0, columnspan=3, sticky="ew", pady=10)
        r += 1
        self.limit = tk.IntVar(value=p.get("limit", 0))
        theme.stitek(obal, "Čas na hráče:").grid(row=r, column=0, sticky="w")
        cas = tk.Frame(obal, bg=B["panel"])
        cas.grid(row=r, column=1, columnspan=2, sticky="w")
        ttk.Spinbox(cas, from_=0, to=180, textvariable=self.limit, width=4).pack(side="left")
        theme.stitek(cas, " minut  (0 = bez limitu)", fg=B["tlumeny"]).pack(side="left")
        r += 1
        self.otacet = tk.BooleanVar(value=p.get("otacet", True))
        ttk.Checkbutton(obal, text="Po každém tahu otočit desku k hráči na tahu", variable=self.otacet).grid(
            row=r, column=1, columnspan=2, sticky="w", pady=(6, 2))
        r += 1

        tl = tk.Frame(obal, bg=B["panel"])
        tl.grid(row=r, column=0, columnspan=3, sticky="e", pady=(14, 0))
        theme.tlacitko(tl, "Zrušit", self.zrus).pack(side="right")
        theme.tlacitko(tl, "Hrát!", self._ok, hlavni=True).pack(side="right", padx=(0, 8))
        self.bind("<Return>", lambda e: self._ok())

    def _cislo(self, var: tk.IntVar, vychozi: int) -> int:
        try:
            return int(var.get())
        except (tk.TclError, ValueError):
            return vychozi

    def _zmena_sirky(self):
        self._vychozi()

    def _vychozi(self):
        s = min(MAX_SIRKA, max(MIN_SIRKA, self._cislo(self.sirka, 8)))
        self.rada.set(vychozi_rada(s))

    def _ok(self):
        sirka = self._cislo(self.sirka, -1)
        vyska = self._cislo(self.vyska, -1)
        limit = self._cislo(self.limit, -1)
        rada = self.rada.get().strip().upper()
        bily, cerny = self.bily.get().strip(), self.cerny.get().strip()
        chyby = []
        if not bily or not cerny:
            chyby.append("Oba hráči musí mít jméno.")
        elif bily == cerny:
            chyby.append("Hráči musí mít různá jména.")
        if not (MIN_SIRKA <= sirka <= MAX_SIRKA) or not (MIN_VYSKA <= vyska <= MAX_VYSKA):
            chyby.append(f"Deska může mít {MIN_SIRKA}–{MAX_SIRKA} sloupců a {MIN_VYSKA}–{MAX_VYSKA} řad.")
        elif len(rada) != sirka:
            chyby.append(f"Základní řada musí mít přesně {sirka} znaků (teď má {len(rada)}).")
        nezname = sorted({z for z in rada if z != '.' and self.registr.get(z) is None})
        if nezname:
            chyby.append("Neznámé figurky: " + ", ".join(nezname))
        if rada.count('K') != 1:
            chyby.append("V základní řadě musí být právě jeden král (K).")
        if limit < 0:
            chyby.append("Časový limit musí být číslo ≥ 0.")
        if chyby:
            messagebox.showerror("Nelze začít", "\n".join(chyby), parent=self)
            return
        self.vysledek = {"bily": bily, "cerny": cerny, "sirka": sirka, "vyska": vyska, "rada": rada,
                         "pesci": self.pesci.get(), "limit": limit, "otacet": self.otacet.get()}
        self.destroy()
