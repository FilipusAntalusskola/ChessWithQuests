import tkinter as tk
from tkinter import ttk, messagebox

from model.kwest import Kwest, TYPY_KWESTU
from view import theme
from view.dialogs import Dialog
from view.theme import B

LIBOVOLNA = "— libovolná —"


class KwestEditor(Dialog):
    """Editor kwestů (úkolů), ukládá do data/kwesty.json."""

    def __init__(self, master, katalog, registr):
        super().__init__(master, "Editor kwestů")
        self.katalog = katalog
        self.registr = registr
        self.editovany: str | None = None

        obal = tk.Frame(self, bg=B["panel"])
        obal.pack(fill="both", expand=True, padx=16, pady=14)

        vlevo = tk.Frame(obal, bg=B["panel"])
        vlevo.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        theme.stitek(vlevo, "Kwesty", theme.H2, fg=B["akcent"]).pack(anchor="w")
        self.seznam = tk.Listbox(vlevo, width=28, height=16, bg=B["panel2"], fg=B["text"], relief="flat",
                                 highlightthickness=0, selectbackground=B["akcent_tmavy"], font=theme.TEXT,
                                 activestyle="none", exportselection=False)
        self.seznam.pack(fill="y", expand=True, pady=6)
        self.seznam.bind("<<ListboxSelect>>", self._vybrano)
        theme.tlacitko(vlevo, "+ Nový kwest", self._novy).pack(fill="x", pady=2)
        theme.tlacitko(vlevo, "Smazat", self._smaz).pack(fill="x", pady=2)

        f = tk.Frame(obal, bg=B["panel"])
        f.grid(row=0, column=1, sticky="nsew")
        self.v_nazev, self.v_popis = tk.StringVar(), tk.StringVar()
        self.v_typ, self.v_kym, self.v_koho = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.v_pocet, self.v_body = tk.IntVar(value=1), tk.IntVar(value=10)
        figurky = [LIBOVOLNA] + [f"{d.znacka} – {d.nazev}" for d in registr.seznam()]
        self._typy = list(TYPY_KWESTU.items())

        radky = [
            ("Název:", theme.vstup(f, textvariable=self.v_nazev, width=34)),
            ("Popis:", theme.vstup(f, textvariable=self.v_popis, width=34)),
            ("Typ:", ttk.Combobox(f, textvariable=self.v_typ, values=[t[1] for t in self._typy],
                                  state="readonly", width=31)),
            ("Počet:", ttk.Spinbox(f, from_=1, to=200, textvariable=self.v_pocet, width=6)),
            ("Kým (vlastní figurka):", ttk.Combobox(f, textvariable=self.v_kym, values=figurky,
                                                    state="readonly", width=31)),
            ("Koho / v co:", ttk.Combobox(f, textvariable=self.v_koho, values=figurky,
                                          state="readonly", width=31)),
            ("Body za splnění:", ttk.Spinbox(f, from_=0, to=1000, textvariable=self.v_body, width=6)),
        ]
        for r, (text, w) in enumerate(radky):
            theme.stitek(f, text).grid(row=r, column=0, sticky="w", pady=3, padx=(0, 8))
            w.grid(row=r, column=1, sticky="w", pady=3)
        napoveda = ("„Počet“ = kolikrát se to musí stát během jedné partie; u typu „Vyhraj do N tahů“\n"
                    "je to maximální počet vlastních tahů.\n"
                    "„Koho / v co“ = vyhozená soupeřova figurka, u proměny figurka, ve kterou se pěšec mění.\n"
                    "Každý kwest může hráč splnit jen jednou – plnění se ukládá k jeho jménu.")
        theme.stitek(f, napoveda, theme.MALY, fg=B["tlumeny"], justify="left").grid(
            row=len(radky), column=0, columnspan=2, sticky="w", pady=(8, 6))
        tl = tk.Frame(f, bg=B["panel"])
        tl.grid(row=len(radky) + 1, column=0, columnspan=2, sticky="e", pady=(6, 0))
        theme.tlacitko(tl, "Zavřít", self.zrus).pack(side="right")
        theme.tlacitko(tl, "Uložit kwest", self._uloz, hlavni=True).pack(side="right", padx=(0, 8))

        self._obnov_seznam()
        if self.katalog.kwesty:
            self.seznam.selection_set(0)
            self._vybrano()
        else:
            self._novy()

    def _obnov_seznam(self, vybrat: str | None = None):
        self.seznam.delete(0, "end")
        for k in self.katalog.kwesty:
            self.seznam.insert("end", f"{k.nazev}  ({k.body} b.)")
        if vybrat:
            ids = [k.id for k in self.katalog.kwesty]
            if vybrat in ids:
                self.seznam.selection_set(ids.index(vybrat))

    def _figurka_text(self, znacka):
        if not znacka:
            return LIBOVOLNA
        d = self.registr.get(znacka)
        return f"{znacka} – {d.nazev}" if d else f"{znacka} – ?"

    def _vybrano(self, _e=None):
        sel = self.seznam.curselection()
        if not sel:
            return
        k = self.katalog.kwesty[sel[0]]
        self.editovany = k.id
        self.v_nazev.set(k.nazev)
        self.v_popis.set(k.popis)
        self.v_typ.set(TYPY_KWESTU.get(k.typ, ""))
        self.v_pocet.set(k.pocet)
        self.v_body.set(k.body)
        self.v_kym.set(self._figurka_text(k.kym))
        self.v_koho.set(self._figurka_text(k.koho))

    def _novy(self):
        self.seznam.selection_clear(0, "end")
        self.editovany = None
        self.v_nazev.set("")
        self.v_popis.set("")
        self.v_typ.set(self._typy[1][1])
        self.v_pocet.set(1)
        self.v_body.set(10)
        self.v_kym.set(LIBOVOLNA)
        self.v_koho.set(LIBOVOLNA)

    def _uloz(self):
        typ = next((kod for kod, popis in self._typy if popis == self.v_typ.get()), None)
        try:
            pocet, body = int(self.v_pocet.get()), int(self.v_body.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Chyba", "Počet a body musí být čísla.", parent=self)
            return

        def znacka(text):
            return None if not text or text == LIBOVOLNA else text[0]

        nazev = self.v_nazev.get().strip()
        kid = self.editovany
        if kid is None:
            zaklad = Kwest.vytvor_id(nazev)
            kid, i = zaklad, 2
            while self.katalog.najdi(kid):
                kid, i = f"{zaklad}_{i}", i + 1
        k = Kwest(nazev, self.v_popis.get().strip(), typ or "", pocet, znacka(self.v_kym.get()),
                  znacka(self.v_koho.get()), body, kid)
        try:
            self.katalog.pridej(k)
            self.katalog.uloz()
        except (ValueError, OSError) as ex:
            messagebox.showerror("Nelze uložit", str(ex), parent=self)
            return
        self.editovany = k.id
        self._obnov_seznam(vybrat=k.id)

    def _smaz(self):
        if self.editovany and messagebox.askyesno("Smazat kwest", "Opravdu smazat vybraný kwest?", parent=self):
            self.katalog.odeber(self.editovany)
            self.katalog.uloz()
            self._obnov_seznam()
            self._novy()
