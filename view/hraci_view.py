import tkinter as tk
from tkinter import ttk, messagebox

from view import theme
from view.dialogs import Dialog
from view.theme import B


class HraciView(Dialog):
    """Přehled hráčů: ELO, statistiky, splněné kwesty."""

    def __init__(self, master, users, katalog):
        super().__init__(master, "Hráči a žebříček")
        self.users = users
        self.katalog = katalog
        obal = tk.Frame(self, bg=B["panel"])
        obal.pack(fill="both", expand=True, padx=16, pady=14)
        theme.stitek(obal, "Žebříček hráčů", theme.H2, fg=B["akcent"]).pack(anchor="w")
        sloupce = (("elo", "ELO", 60), ("partie", "Partie", 60), ("vyhry", "Výhry", 60),
                   ("remizy", "Remízy", 60), ("prohry", "Prohry", 60), ("kwesty", "Kwesty", 70),
                   ("body", "Body", 60))
        self.strom = ttk.Treeview(obal, columns=[s[0] for s in sloupce], height=12)
        self.strom.heading("#0", text="Hráč")
        self.strom.column("#0", width=170)
        for kod, nazev, sirka in sloupce:
            self.strom.heading(kod, text=nazev)
            self.strom.column(kod, width=sirka, anchor="center")
        self.strom.pack(fill="both", expand=True, pady=8)
        self.strom.bind("<<TreeviewSelect>>", self._detail)
        self.detail = theme.stitek(obal, "Vyber hráče a uvidíš jeho splněné kwesty.", theme.MALY,
                                   fg=B["tlumeny"], wraplength=640, justify="left", anchor="w")
        self.detail.pack(fill="x")
        tl = tk.Frame(obal, bg=B["panel"])
        tl.pack(fill="x", pady=(10, 0))
        theme.tlacitko(tl, "Zavřít", self.zrus).pack(side="right")
        theme.tlacitko(tl, "Smazat hráče", self._smaz).pack(side="left")
        self._obnov()

    def _obnov(self):
        self.strom.delete(*self.strom.get_children())
        for u in sorted(self.users.uzivatele.values(), key=lambda u: (-u.elo, u.uzivatelske_jmeno.lower())):
            self.strom.insert("", "end", iid=u.uzivatelske_jmeno, text=u.uzivatelske_jmeno,
                              values=(u.elo, u.partie, u.vyhry, u.remizy, u.prohry, len(u.splnene_kvesty), u.body))

    def _detail(self, _e=None):
        sel = self.strom.selection()
        if not sel:
            return
        u = self.users.najdi(sel[0])
        nazvy = [self.katalog.najdi(k).nazev if self.katalog.najdi(k) else k for k in u.splnene_kvesty]
        self.detail.config(text=f"{u.uzivatelske_jmeno}: " + (", ".join(nazvy) if nazvy else "zatím žádné kwesty"))

    def _smaz(self):
        sel = self.strom.selection()
        if sel and messagebox.askyesno("Smazat hráče", f"Smazat hráče {sel[0]} i s historií?", parent=self):
            self.users.smaz(sel[0])
            self.users.uloz()
            self._obnov()
