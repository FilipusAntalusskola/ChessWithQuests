import tkinter as tk
from tkinter import ttk, messagebox

from model.definice_figurek import DefiniceFigurky, parse_pohyby, format_pohyby
from model.figurka import DefinovanaFigurka, VESTAVENE_TRIDY
from model.herni_plocha import Herni_Plocha
from model.pol import Pol
from model.revizor_tahu import RevizorTahu
from model.tah import Tah
from view import theme
from view.dialogs import Dialog
from view.theme import B

NAPOVEDA = (
    "Jeden řádek = skupina vektorů:   vektory ; dosah ; vpřed\n"
    "• vektory: dx,dy oddělené mezerou (z pohledu bílého, dy>0 = dopředu)\n"
    "• dosah: kolikrát se vektor smí opakovat, 0 = neomezeně\n"
    "• vpřed: jen tímto směrem (jinak i opačně)\n"
    "Příklad jezdce:  1,2 1,-2 2,1 2,-1 ; 1"
)
NAHLED = 11     # velikost náhledové desky


class FigurkaEditor(Dialog):
    """Editor vlastních figurek s živým náhledem pohybu."""

    def __init__(self, master, registr):
        super().__init__(master, "Editor figurek")
        self.registr = registr
        self.editovana: str | None = None
        self.resizable(True, True)

        obal = tk.Frame(self, bg=B["panel"])
        obal.pack(fill="both", expand=True, padx=16, pady=14)

        # --- seznam ---
        vlevo = tk.Frame(obal, bg=B["panel"])
        vlevo.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        theme.stitek(vlevo, "Figurky", theme.H2, fg=B["akcent"]).pack(anchor="w")
        self.seznam = tk.Listbox(vlevo, width=24, height=18, bg=B["panel2"], fg=B["text"], relief="flat",
                                 highlightthickness=0, selectbackground=B["akcent_tmavy"], font=theme.TEXT,
                                 activestyle="none", exportselection=False)
        self.seznam.pack(fill="y", expand=True, pady=6)
        self.seznam.bind("<<ListboxSelect>>", self._vybrano)
        theme.tlacitko(vlevo, "+ Nová figurka", self._nova).pack(fill="x", pady=2)
        self.btn_smazat = theme.tlacitko(vlevo, "Smazat", self._smaz)
        self.btn_smazat.pack(fill="x", pady=2)

        # --- formulář ---
        stred = tk.Frame(obal, bg=B["panel"])
        stred.grid(row=0, column=1, sticky="nsew")
        obal.columnconfigure(1, weight=1)
        obal.rowconfigure(0, weight=1)

        self.v_znacka = tk.StringVar()
        self.v_nazev = tk.StringVar()
        self.v_symbol = tk.StringVar()
        self.v_popis = tk.StringVar()
        self.v_skok = tk.BooleanVar()
        r = 0
        theme.stitek(stred, "Značka:").grid(row=r, column=0, sticky="w")
        radek = tk.Frame(stred, bg=B["panel"])
        radek.grid(row=r, column=1, sticky="ew", pady=2)
        self.e_znacka = theme.vstup(radek, textvariable=self.v_znacka, width=4)
        self.e_znacka.pack(side="left")
        theme.stitek(radek, "  Název:").pack(side="left")
        self.e_nazev = theme.vstup(radek, textvariable=self.v_nazev, width=18)
        self.e_nazev.pack(side="left")
        theme.stitek(radek, "  Symbol:").pack(side="left")
        self.e_symbol = theme.vstup(radek, textvariable=self.v_symbol, width=4)
        self.e_symbol.pack(side="left")
        r += 1
        theme.stitek(stred, "Popis:").grid(row=r, column=0, sticky="w")
        self.e_popis = theme.vstup(stred, textvariable=self.v_popis)
        self.e_popis.grid(row=r, column=1, sticky="ew", pady=2)
        r += 1
        theme.stitek(stred, "Pohyby:").grid(row=r, column=0, sticky="nw", pady=(6, 0))
        self.t_pohyby = theme.textove_pole(stred, height=5, width=42)
        self.t_pohyby.grid(row=r, column=1, sticky="ew", pady=(6, 2))
        r += 1
        theme.stitek(stred, "Útoky:").grid(row=r, column=0, sticky="nw")
        self.t_utoky = theme.textove_pole(stred, height=3, width=42)
        self.t_utoky.grid(row=r, column=1, sticky="ew", pady=2)
        r += 1
        theme.stitek(stred, "(prázdné = bere stejně, jak se pohybuje)", theme.MALY, fg=B["tlumeny"]).grid(
            row=r, column=1, sticky="w")
        r += 1
        self.c_skok = ttk.Checkbutton(stred, text="Přeskakuje figurky (jako jezdec)", variable=self.v_skok,
                                      command=self._nahled)
        self.c_skok.grid(row=r, column=1, sticky="w", pady=4)
        r += 1
        theme.stitek(stred, NAPOVEDA, theme.MALY, fg=B["tlumeny"], justify="left").grid(
            row=r, column=1, sticky="w", pady=(4, 6))
        r += 1
        self.chyba = theme.stitek(stred, "", theme.MALY, fg=B["chyba"], justify="left", wraplength=380)
        self.chyba.grid(row=r, column=1, sticky="w")
        r += 1
        tl = tk.Frame(stred, bg=B["panel"])
        tl.grid(row=r, column=1, sticky="e", pady=(8, 0))
        theme.tlacitko(tl, "Zavřít", self.zrus).pack(side="right")
        self.btn_ulozit = theme.tlacitko(tl, "Uložit figurku", self._uloz, hlavni=True)
        self.btn_ulozit.pack(side="right", padx=(0, 8))
        stred.columnconfigure(1, weight=1)

        # --- náhled ---
        vpravo = tk.Frame(obal, bg=B["panel"])
        vpravo.grid(row=0, column=2, sticky="n", padx=(14, 0))
        theme.stitek(vpravo, "Náhled pohybu", theme.H2, fg=B["akcent"]).pack(anchor="w")
        self.nahled = tk.Canvas(vpravo, width=NAHLED * 26, height=NAHLED * 26, bg=B["okraj"],
                                highlightthickness=0)
        self.nahled.pack(pady=6)
        legenda = tk.Frame(vpravo, bg=B["panel"])
        legenda.pack(anchor="w")
        c = tk.Canvas(legenda, width=14, height=14, bg=B["panel"], highlightthickness=0)
        c.create_oval(3, 3, 11, 11, fill=B["tecka"], outline="")
        c.pack(side="left")
        theme.stitek(legenda, " tah   ", theme.MALY).pack(side="left")
        c = tk.Canvas(legenda, width=14, height=14, bg=B["panel"], highlightthickness=0)
        c.create_line(3, 3, 11, 11, fill=B["sach"], width=2)
        c.create_line(11, 3, 3, 11, fill=B["sach"], width=2)
        c.pack(side="left")
        theme.stitek(legenda, " braní", theme.MALY).pack(side="left")
        theme.stitek(vpravo, "Bílý táhne nahoru.", theme.MALY, fg=B["tlumeny"]).pack(anchor="w")

        for w in (self.t_pohyby, self.t_utoky, self.e_znacka, self.e_symbol):
            w.bind("<KeyRelease>", lambda e: self._nahled())

        self._obnov_seznam()
        self.seznam.selection_set(0)
        self._vybrano()

    # ---------------------------------------------------------------- seznam
    def _obnov_seznam(self, vybrat: str | None = None):
        self.seznam.delete(0, "end")
        self._znacky = []
        for d in self.registr.seznam():
            zamek = "  (vestavěná)" if d.vestavena else ""
            self.seznam.insert("end", f"{d.znacka}  {d.nazev}{zamek}")
            self._znacky.append(d.znacka)
        if vybrat in self._znacky:
            i = self._znacky.index(vybrat)
            self.seznam.selection_clear(0, "end")
            self.seznam.selection_set(i)
            self.seznam.see(i)

    def _vybrano(self, _e=None):
        sel = self.seznam.curselection()
        if not sel:
            return
        d = self.registr.get(self._znacky[sel[0]])
        self._nacti_formular(d)

    def _nacti_formular(self, d: DefiniceFigurky | None):
        self.editovana = d.znacka if d and not d.vestavena else None
        vestavena = bool(d and d.vestavena)
        stav = "disabled" if vestavena else "normal"
        for e in (self.e_znacka, self.e_nazev, self.e_symbol, self.e_popis, self.t_pohyby, self.t_utoky):
            e.config(state="normal")
        self.v_znacka.set(d.znacka if d else "")
        self.v_nazev.set(d.nazev if d else "")
        self.v_symbol.set(d.symbol if d else "")
        self.v_popis.set(d.popis if d else "")
        self.v_skok.set(d.skok if d else False)
        self.t_pohyby.delete("1.0", "end")
        self.t_utoky.delete("1.0", "end")
        if d:
            self.t_pohyby.insert("1.0", format_pohyby(d.pohyby))
            self.t_utoky.insert("1.0", format_pohyby(d.utoky))
        for e in (self.e_znacka, self.e_nazev, self.e_symbol, self.e_popis, self.t_pohyby, self.t_utoky):
            e.config(state=stav)
        self.c_skok.state(["disabled"] if vestavena else ["!disabled"])
        self.btn_ulozit.config(state=stav)
        self.btn_smazat.config(state=stav if d else "disabled")
        self._nahled()

    def _nova(self):
        self.seznam.selection_clear(0, "end")
        volne = next((z for z in "ABCEFGHILMNOQRTUWXYZ" if self.registr.get(z) is None), "")
        self._nacti_formular(None)
        self.v_znacka.set(volne)
        self.t_pohyby.insert("1.0", "0,1 1,0 ; 2")
        self.e_nazev.focus_set()
        self._nahled()

    # ---------------------------------------------------------------- definice z formuláře
    def _definice_z_formulare(self) -> DefiniceFigurky:
        znacka = self.v_znacka.get().strip().upper()
        pohyby = parse_pohyby(self.t_pohyby.get("1.0", "end"))
        utoky = parse_pohyby(self.t_utoky.get("1.0", "end"))
        if len(znacka) != 1 or not znacka.isalpha():
            raise ValueError("Značka musí být jedno písmeno.")
        if not pohyby:
            raise ValueError("Zadej aspoň jeden pohyb.")
        symbol = self.v_symbol.get().strip()[:2]
        return DefiniceFigurky(znacka, self.v_nazev.get().strip() or "?", pohyby, utoky, self.v_skok.get(),
                               symbol, self.v_popis.get().strip())

    def _nahled(self):
        c = self.nahled
        c.delete("all")
        s = 26
        for x in range(NAHLED):
            for y in range(NAHLED):
                barva = B["svetle_pole"] if (x + y) % 2 == 0 else B["tmave_pole"]
                c.create_rectangle(x * s, y * s, x * s + s, y * s + s, fill=barva, outline="")
        sel = self.seznam.curselection()
        try:
            if sel and self.registr.get(self._znacky[sel[0]]).vestavena:
                fig = VESTAVENE_TRIDY[self._znacky[sel[0]]](1)
            else:
                fig = DefinovanaFigurka(self._definice_z_formulare(), 1)
            self.chyba.config(text="")
        except ValueError as ex:
            self.chyba.config(text=str(ex))
            return
        plocha = Herni_Plocha((NAHLED, NAHLED))
        stred = Pol(NAHLED // 2 + 1, NAHLED // 2 + 1)
        plocha.setFigurku(fig, stred)

        def na_xy(p):
            return (p.getSloupec() - 1) * s, (NAHLED - p.getRad()) * s

        for cil in fig.getAllReachable(stred, plocha.rozmery):
            rev = RevizorTahu(plocha, Tah(stred, cil, fig))
            tah = rev.getBaseVektor(utok=False) is not None
            brani = rev.getBaseVektor(utok=True) is not None
            x, y = na_xy(cil)
            if tah:
                c.create_oval(x + 8, y + 8, x + s - 8, y + s - 8, fill=B["tecka"], outline="")
            if brani and (not tah or fig.getVektoryUtoku() != fig.getVektory()):
                c.create_line(x + 6, y + 6, x + s - 6, y + s - 6, fill=B["sach"], width=2)
                c.create_line(x + s - 6, y + 6, x + 6, y + s - 6, fill=B["sach"], width=2)
        x, y = na_xy(stred)
        theme.nakresli_figurku(c, fig, x + s / 2, y + s / 2, s)

    # ---------------------------------------------------------------- uložení / smazání
    def _uloz(self):
        try:
            d = self._definice_z_formulare()
        except ValueError as ex:
            messagebox.showerror("Chyba v definici", str(ex), parent=self)
            return
        if d.znacka in VESTAVENE_TRIDY:
            messagebox.showerror("Chyba", f"Značka {d.znacka} patří vestavěné figurce.", parent=self)
            return
        existujici = self.registr.get(d.znacka)
        if existujici is not None and d.znacka != self.editovana:
            if not messagebox.askyesno("Přepsat?", f"Figurka se značkou {d.znacka} ({existujici.nazev}) "
                                                   f"už existuje. Přepsat ji?", parent=self):
                return
        try:
            if self.editovana and self.editovana != d.znacka and self.registr.get(self.editovana):
                self.registr.odeber(self.editovana)
            self.registr.pridej(d)
            self.registr.uloz()
        except (ValueError, OSError) as ex:
            messagebox.showerror("Nelze uložit", str(ex), parent=self)
            return
        self.editovana = d.znacka
        self._obnov_seznam(vybrat=d.znacka)

    def _smaz(self):
        if not self.editovana:
            return
        d = self.registr.get(self.editovana)
        if d and messagebox.askyesno("Smazat figurku", f"Opravdu smazat figurku {d.nazev}?", parent=self):
            self.registr.odeber(d.znacka)
            self.registr.uloz()
            self._obnov_seznam()
            self.seznam.selection_set(0)
            self._vybrano()
