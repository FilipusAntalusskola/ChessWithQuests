import tkinter as tk
from tkinter import ttk

from view import theme
from view.board_view import BoardView
from view.theme import B


class KartaHrace(tk.Frame):
    """Panel jednoho hráče: jméno, ELO, body, hodiny, vyhozené figurky."""

    def __init__(self, master, barva: int):
        super().__init__(master, bg=B["panel2"], highlightthickness=2, highlightbackground=B["panel2"])
        self.barva = barva
        horni = tk.Frame(self, bg=B["panel2"])
        horni.pack(fill="x", padx=10, pady=(8, 2))
        kolecko = tk.Canvas(horni, width=18, height=18, bg=B["panel2"], highlightthickness=0)
        kolecko.create_oval(2, 2, 16, 16, fill=B["bila"] if barva == 1 else B["cerna"], outline=B["akcent"])
        kolecko.pack(side="left")
        self.jmeno = theme.stitek(horni, "", theme.H2, bg=B["panel2"])
        self.jmeno.pack(side="left", padx=6)
        self.hodiny = theme.stitek(horni, "0:00", theme.HODINY, bg=B["panel2"])
        self.hodiny.pack(side="right")
        self.info = theme.stitek(self, "", theme.MALY, fg=B["tlumeny"], bg=B["panel2"], anchor="w")
        self.info.pack(fill="x", padx=10)
        self.vyhozene = tk.Canvas(self, height=26, bg=B["panel2"], highlightthickness=0)
        self.vyhozene.pack(fill="x", padx=8, pady=(2, 8))

    def nastav(self, jmeno: str, info: str, cas: str, vyhozene: list, aktivni: bool, malo_casu: bool):
        self.jmeno.config(text=jmeno)
        self.info.config(text=info)
        self.hodiny.config(text=cas, fg=B["chyba"] if malo_casu else (B["akcent"] if aktivni else B["text"]))
        self.config(highlightbackground=B["akcent"] if aktivni else B["panel2"])
        self.vyhozene.delete("all")
        x = 12
        for fig in vyhozene:
            theme.nakresli_figurku(self.vyhozene, fig, x, 13, 24)
            x += 17

    def nastav_cas(self, cas: str, aktivni: bool, malo_casu: bool):
        self.hodiny.config(text=cas, fg=B["chyba"] if malo_casu else (B["akcent"] if aktivni else B["text"]))


class GameView(tk.Frame):
    """Obrazovka partie: deska vlevo, panel vpravo. Akce předává controlleru."""

    def __init__(self, master, controller):
        super().__init__(master, bg=B["pozadi"])
        self.c = controller
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.deska = BoardView(self, controller.klik)
        self.deska.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=12)

        panel = tk.Frame(self, bg=B["panel"], width=350)
        panel.grid(row=0, column=1, sticky="ns", padx=(6, 12), pady=12)
        panel.grid_propagate(False)
        panel.pack_propagate(False)
        self.panel = panel

        self.na_tahu = theme.stitek(panel, "", ("Georgia", 14, "bold"), fg=B["akcent"], wraplength=320,
                                    justify="left", anchor="w")
        self.na_tahu.pack(fill="x", padx=12, pady=(12, 8))

        self.karty = {-1: KartaHrace(panel, -1), 1: KartaHrace(panel, 1)}
        self.karty[-1].pack(fill="x", padx=12, pady=(0, 6))
        self.karty[1].pack(fill="x", padx=12, pady=(0, 8))

        # tlačítka
        tl = tk.Frame(panel, bg=B["panel"])
        tl.pack(side="bottom", fill="x", padx=12, pady=(6, 12))
        for i in range(2):
            tl.columnconfigure(i, weight=1)
        self.btn_zpet = theme.tlacitko(tl, "↶ Tah zpět", controller.tah_zpet)
        self.btn_otoc = theme.tlacitko(tl, "⟲ Otočit desku", controller.otoc)
        self.btn_remiza = theme.tlacitko(tl, "½ Nabídnout remízu", controller.remiza)
        self.btn_vzdat = theme.tlacitko(tl, "⚑ Vzdát se", controller.vzdat)
        self.btn_pgn = theme.tlacitko(tl, "Uložit partii (PGN)", controller.uloz_pgn)
        self.btn_menu = theme.tlacitko(tl, "Do menu", controller.do_menu)
        self.btn_odveta = theme.tlacitko(tl, "Odveta (prohodit barvy)", controller.odveta, hlavni=True)
        for i, b in enumerate((self.btn_zpet, self.btn_otoc, self.btn_remiza, self.btn_vzdat,
                               self.btn_pgn, self.btn_menu)):
            b.grid(row=i // 2, column=i % 2, sticky="ew", padx=2, pady=2)

        # oznámení o splněných kwestech
        self.toasty = tk.Frame(panel, bg=B["panel"])
        self.toasty.pack(side="bottom", fill="x", padx=12)

        # záložky: tahy / kwesty
        nb = ttk.Notebook(panel)
        nb.pack(fill="both", expand=True, padx=12, pady=(0, 6))
        self.notebook = nb

        f_tahy = tk.Frame(nb, bg=B["panel2"])
        self.seznam_tahu = tk.Listbox(f_tahy, bg=B["panel2"], fg=B["text"], font=("Consolas", 11),
                                      relief="flat", highlightthickness=0, activestyle="none",
                                      selectbackground=B["akcent_tmavy"])
        sb = ttk.Scrollbar(f_tahy, orient="vertical", command=self.seznam_tahu.yview)
        self.seznam_tahu.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.seznam_tahu.pack(fill="both", expand=True, padx=4, pady=4)
        nb.add(f_tahy, text="Tahy")

        f_kw = tk.Frame(nb, bg=B["panel2"])
        self.strom_kwestu = ttk.Treeview(f_kw, columns=("b", "c"), show="tree headings", height=6)
        self.strom_kwestu.heading("#0", text="Kwest")
        self.strom_kwestu.heading("b", text="Bílý")
        self.strom_kwestu.heading("c", text="Černý")
        self.strom_kwestu.column("#0", width=170, stretch=True)
        self.strom_kwestu.column("b", width=62, anchor="center", stretch=False)
        self.strom_kwestu.column("c", width=62, anchor="center", stretch=False)
        self.strom_kwestu.tag_configure("ted", foreground=B["akcent"])
        self.strom_kwestu.tag_configure("drive", foreground=B["tlumeny"])
        self.strom_kwestu.bind("<<TreeviewSelect>>", self._vyber_kwestu)
        self.strom_kwestu.pack(fill="both", expand=True, padx=4, pady=(4, 0))
        self.popis_kwestu = theme.stitek(f_kw, "Klikni na kwest pro popis.", theme.MALY, fg=B["tlumeny"],
                                         bg=B["panel2"], wraplength=300, justify="left", anchor="w")
        self.popis_kwestu.pack(fill="x", padx=6, pady=6)
        nb.add(f_kw, text="Kwesty")
        self._popisy: dict[str, str] = {}
        self._casovace: list[str] = []

    # --- aktualizace z controlleru ---
    def nastav_na_tahu(self, text: str, barva_textu: str | None = None):
        self.na_tahu.config(text=text, fg=barva_textu or B["akcent"])

    def nastav_hrace(self, barva: int, *args):
        self.karty[barva].nastav(*args)

    def nastav_cas(self, barva: int, *args):
        self.karty[barva].nastav_cas(*args)

    def poradi_karet(self, otoceno: bool):
        # Hráč, který sedí "dole" u desky, má kartu dole
        horni, dolni = (1, -1) if otoceno else (-1, 1)
        self.karty[horni].pack_forget()
        self.karty[dolni].pack_forget()
        self.karty[horni].pack(fill="x", padx=12, pady=(0, 6), after=self.na_tahu)
        self.karty[dolni].pack(fill="x", padx=12, pady=(0, 8), after=self.karty[horni])

    def nastav_tahy(self, radky: list[str]):
        self.seznam_tahu.delete(0, "end")
        for r in radky:
            self.seznam_tahu.insert("end", r)
        self.seznam_tahu.see("end")

    def nastav_kwesty(self, radky: list[tuple[str, str, str, str, str, str]]):
        """radky: (id, název, stav bílý, stav černý, tag, popis)"""
        vybrany = self.strom_kwestu.selection()
        self.strom_kwestu.delete(*self.strom_kwestu.get_children())
        self._popisy = {}
        for kid, nazev, sb, sc, tag, popis in radky:
            self.strom_kwestu.insert("", "end", iid=kid, text=nazev, values=(sb, sc), tags=(tag,) if tag else ())
            self._popisy[kid] = popis
        if vybrany and vybrany[0] in self._popisy:
            self.strom_kwestu.selection_set(vybrany[0])

    def _vyber_kwestu(self, _event=None):
        sel = self.strom_kwestu.selection()
        if sel:
            self.popis_kwestu.config(text=self._popisy.get(sel[0], ""))

    def rezim_konec(self, konec: bool):
        stav = "disabled" if konec else "normal"
        for b in (self.btn_zpet, self.btn_remiza, self.btn_vzdat):
            b.config(state=stav)
        if konec:
            self.btn_odveta.grid(row=3, column=0, columnspan=2, sticky="ew", padx=2, pady=(6, 2))
        else:
            self.btn_odveta.grid_remove()

    def toast(self, text: str, zlaty: bool = True, doba_ms: int = 5000):
        lbl = tk.Label(self.toasty, text=text, font=theme.TEXT_B, wraplength=310, justify="left", anchor="w",
                       bg=B["akcent"] if zlaty else B["okraj"], fg=B["cerna"] if zlaty else B["text"],
                       padx=10, pady=6)
        lbl.pack(fill="x", pady=2)
        self._casovace.append(self.after(doba_ms, lbl.destroy))

    def destroy(self):
        for aid in self._casovace:
            try:
                self.after_cancel(aid)
            except tk.TclError:
                pass
        super().destroy()
