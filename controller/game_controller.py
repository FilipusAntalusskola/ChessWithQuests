from tkinter import messagebox, filedialog

from model.chess_notation_formatter import ChessNotationFormatter_SanCz
from model.figurka import Pesak
from model.game_logger import GameLogger
from model.game_manager import GameManager, MAT, PAT, VZDANO, REMIZA, CAS
from model.game_timer import GameTimer
from model.herni_plocha import Herni_Plocha
from model.hrac import Hrac
from model.kwest_manager import KwestManager
from model.pol import Pol
from view.dialogs import PromenaDialog
from view.game_view import GameView
from view.theme import B


class GameController:
    """Propojuje GameManager (model) a GameView (view) jedné partie."""

    def __init__(self, app, cfg: dict):
        self.app = app
        self.cfg = cfg
        plocha = Herni_Plocha((cfg["sirka"], cfg["vyska"])).populate(cfg["rada"], app.registr, cfg["pesci"])
        ub, uc = app.users.ziskej(cfg["bily"]), app.users.ziskej(cfg["cerny"])
        km = KwestManager(app.katalog.kwesty, [set(ub.splnene_kvesty), set(uc.splnene_kvesty)])
        self.gm = GameManager(plocha, [Hrac(1, ub), Hrac(-1, uc)], km, GameTimer(cfg["limit"] * 60),
                              GameLogger(), app.registr)
        self.formatter = ChessNotationFormatter_SanCz()
        self.vyber: Pol | None = None
        self.cile: dict[Pol, object] = {}
        self.rucne_otoceno = False
        self.vysledky_ulozeny = False
        self._tick_id = None

        self.view = GameView(app.root, self)
        app.zobraz(self.view)
        self.obnov()
        self.view.toast(f"{ub.uzivatelske_jmeno} (bílý) proti {uc.uzivatelske_jmeno} (černý). Hodně štěstí!",
                        zlaty=False)
        self._tick()

    # ------------------------------------------------------------ pomocné
    def otoceno(self) -> bool:
        zaklad = self.cfg.get("otacet") and self.gm.aktivni_barva() == -1
        return bool(zaklad) != self.rucne_otoceno

    def _jmeno(self, idx: int) -> str:
        return self.gm.hraci[idx].getJmeno()

    def _zrus_vyber(self):
        self.vyber = None
        self.cile = {}

    # ------------------------------------------------------------ vstup z desky
    def klik(self, pol: Pol):
        if self.gm.je_konec():
            return
        if self.vyber is not None and pol in self.cile:
            self._tahni(self.vyber, pol)
            return
        fig = self.gm.plocha.vrat_obsah(pol)
        if fig is not None and fig.getBarvu() == self.gm.aktivni_barva() and pol != self.vyber:
            self.vyber = pol
            self.cile = {t.getCil(): t for t in self.gm.mozne_tahy_z(pol)}
            if not self.cile:
                self.view.toast(f"{fig.getNazev()} teď nemůže táhnout.", zlaty=False, doba_ms=2500)
        else:
            self._zrus_vyber()
        self.obnov_desku()

    def _tahni(self, start: Pol, cil: Pol):
        nahrad = None
        if self.gm.vyzaduje_promenu(start, cil):
            nahrad = PromenaDialog(self.app.root, self.app.registr, self.gm.aktivni_barva()).ukaz()
            if nahrad is None:
                return          # hráč si to rozmyslel – výběr zůstane
        vysledek = self.gm.proved_tah(start, cil, nahrad)
        self._zrus_vyber()
        if vysledek is None:
            self.view.toast("Neplatný tah.", zlaty=False, doba_ms=2500)
            self.obnov()
            return
        self._oznam_kwesty(vysledek.nove_kwesty)
        self.obnov()
        if vysledek.konec:
            self._konec_hry()

    def _oznam_kwesty(self, nove):
        for idx, k in nove:
            self.view.toast(f"★ {self._jmeno(idx)} splnil(a) kwest „{k.nazev}“ (+{k.body} b.)")

    # ------------------------------------------------------------ tlačítka
    def tah_zpet(self):
        if self.gm.zrus_tah():
            self._zrus_vyber()
            self.obnov()
        else:
            self.view.toast("Není co vracet.", zlaty=False, doba_ms=2500)

    def otoc(self):
        self.rucne_otoceno = not self.rucne_otoceno
        self.obnov()

    def remiza(self):
        if self.gm.je_konec():
            return
        navrhuje = self.gm.aktivni_hrac
        if messagebox.askyesno("Nabídka remízy", f"{self._jmeno(navrhuje)} nabízí remízu.\n\n"
                                                 f"{self._jmeno(1 - navrhuje)}, přijímáš?", parent=self.app.root):
            self._oznam_kwesty(self.gm.remiza())
            self.obnov()
            self._konec_hry()
        else:
            self.view.toast("Remíza odmítnuta, hraje se dál.", zlaty=False, doba_ms=3000)

    def vzdat(self):
        if self.gm.je_konec():
            return
        idx = self.gm.aktivni_hrac
        if messagebox.askyesno("Vzdát se", f"{self._jmeno(idx)}, opravdu se vzdáváš?", parent=self.app.root):
            self._oznam_kwesty(self.gm.vzdat(idx))
            self.obnov()
            self._konec_hry()

    def uloz_pgn(self):
        nazev = filedialog.asksaveasfilename(
            parent=self.app.root, title="Uložit partii", defaultextension=".pgn",
            initialfile=f"{self._jmeno(0)}_vs_{self._jmeno(1)}.pgn",
            filetypes=[("Partie PGN", "*.pgn"), ("Textový soubor", "*.txt"), ("Všechny soubory", "*.*")])
        if not nazev:
            return
        try:
            with open(nazev, "w", encoding="utf-8") as f:
                self.gm.export_pgn(f, self.cfg["rada"])
            self.view.toast("Partie uložena.", zlaty=False, doba_ms=3000)
        except OSError as ex:
            messagebox.showerror("Chyba", f"Soubor se nepodařilo uložit:\n{ex}", parent=self.app.root)

    def do_menu(self):
        if not self.gm.je_konec() and not messagebox.askyesno(
                "Do menu", "Partie ještě běží. Opravdu odejít?\n(Splněné kwesty se uloží, ELO se nemění.)",
                parent=self.app.root):
            return
        self.ukonci()
        self.app.zobraz_menu()

    def odveta(self):
        cfg = dict(self.cfg)
        cfg["bily"], cfg["cerny"] = self.cfg["cerny"], self.cfg["bily"]
        self.ukonci()
        self.app.spust_hru(cfg)

    # ------------------------------------------------------------ konec partie
    def _uloz_kwesty(self):
        km = self.gm.kwest_manager
        for idx, hrac in enumerate(self.gm.hraci):
            for kid in km.splnene_ted[idx]:
                k = self.app.katalog.najdi(kid)
                hrac.uzivatel.pridej_kwest(kid, k.body if k else 0)
        km.splnene_drive = [set(h.uzivatel.splnene_kvesty) for h in self.gm.hraci]
        km.splnene_ted = [[], []]

    def _konec_hry(self):
        if self.vysledky_ulozeny:
            return
        self.vysledky_ulozeny = True
        self._zastav_tick()
        gm = self.gm
        body_ted = [gm.kwest_manager.body_ted(i) for i in (0, 1)]
        self._uloz_kwesty()
        bily, cerny = gm.hraci[0].uzivatel, gm.hraci[1].uzivatel
        d_b, d_c = self.app.users.zapis_vysledek(bily, cerny, gm.skore_bileho())
        try:
            self.app.users.uloz()
        except OSError as ex:
            messagebox.showwarning("Upozornění", f"Výsledky se nepodařilo uložit:\n{ex}", parent=self.app.root)
        self.obnov()
        text = self._text_vysledku() + "\n\n"
        text += f"{bily.uzivatelske_jmeno}: ELO {bily.elo} ({d_b:+d}), kwesty v partii +{body_ted[0]} b.\n"
        text += f"{cerny.uzivatelske_jmeno}: ELO {cerny.elo} ({d_c:+d}), kwesty v partii +{body_ted[1]} b."
        messagebox.showinfo("Konec partie", text, parent=self.app.root)

    def _text_vysledku(self) -> str:
        gm = self.gm
        v = gm.vitez
        if gm.stav == MAT:
            return f"Šach mat! Vítězí {self._jmeno(v)}."
        if gm.stav == PAT:
            return "Pat – remíza."
        if gm.stav == VZDANO:
            return f"{self._jmeno(1 - v)} se vzdal(a). Vítězí {self._jmeno(v)}."
        if gm.stav == REMIZA:
            return "Remíza dohodou."
        if gm.stav == CAS:
            return f"{self._jmeno(1 - v)}: vypršel čas. Vítězí {self._jmeno(v)}."
        return ""

    def ukonci(self):
        """Volá se při odchodu z obrazovky partie."""
        self._zastav_tick()
        if not self.vysledky_ulozeny:
            self._uloz_kwesty()
            try:
                self.app.users.uloz()
            except OSError:
                pass
            self.vysledky_ulozeny = True

    # ------------------------------------------------------------ hodiny
    def _tick(self):
        nove = self.gm.kontrola_casu()
        if nove is not None:
            self._oznam_kwesty(nove)
            self.obnov()
            self._konec_hry()
            return
        self._obnov_hodiny()
        self._tick_id = self.view.after(250, self._tick)

    def _zastav_tick(self):
        if self._tick_id is not None:
            try:
                self.view.after_cancel(self._tick_id)
            except Exception:
                pass
            self._tick_id = None

    def _obnov_hodiny(self):
        gm = self.gm
        for idx, hrac in enumerate(gm.hraci):
            zbyva = gm.casovac.zbyva(idx)
            aktivni = idx == gm.aktivni_hrac and not gm.je_konec()
            self.view.nastav_cas(hrac.getBarvu(), gm.casovac.format(idx), aktivni,
                                 zbyva is not None and zbyva < 30)

    # ------------------------------------------------------------ překreslení
    def obnov(self):
        self.obnov_desku()
        self.obnov_panel()

    def obnov_desku(self):
        gm = self.gm
        brani = set()
        for cil, tah in self.cile.items():
            if gm.plocha.isFigurka(cil) or (isinstance(tah.getFigurku(), Pesak)
                                            and cil.getSloupec() != tah.getStart().getSloupec()):
                brani.add(cil)
        posledni = gm.posledni_tah()
        self.view.deska.nastav(gm.plocha, self.otoceno(), self.vyber, self.cile.keys(), brani,
                               (posledni.getStart(), posledni.getCil()) if posledni else None,
                               self._sach_pol())
        self.view.poradi_karet(self.otoceno())

    def _sach_pol(self) -> Pol | None:
        gm = self.gm
        if gm.stav == MAT:
            return gm.plocha.najdi_krale(-gm.hraci[gm.vitez].getBarvu())
        return None if gm.je_konec() else gm.je_sach()

    def obnov_panel(self):
        gm = self.gm
        km = gm.kwest_manager
        if gm.je_konec():
            self.view.nastav_na_tahu(self._text_vysledku())
        else:
            h = gm.hraci[gm.aktivni_hrac]
            text = f"Na tahu: {h.getJmeno()} ({h.nazev_barvy().lower()})"
            if gm.je_sach():
                self.view.nastav_na_tahu(text + " – ŠACH!", B["chyba"])
            else:
                self.view.nastav_na_tahu(text)
        for idx, hrac in enumerate(gm.hraci):
            u = hrac.uzivatel
            body = u.body + km.body_ted(idx)
            zbyva = gm.casovac.zbyva(idx)
            self.view.nastav_hrace(hrac.getBarvu(), u.uzivatelske_jmeno, f"ELO {u.elo}  ·  {body} bodů za kwesty",
                                   gm.casovac.format(idx),
                                   gm.plocha.getVyhozeneFigurky(-hrac.getBarvu()),
                                   idx == gm.aktivni_hrac and not gm.je_konec(),
                                   zbyva is not None and zbyva < 30)
        radky = []
        for i, (t0, t1) in enumerate(gm.game_logger.getTahy()):
            s0 = self.formatter.toStr(t0) if t0 else "…"
            s1 = self.formatter.toStr(t1) if t1 else ""
            radky.append(f"{i + 1:>3}.  {s0:<10} {s1}")
        self.view.nastav_tahy(radky)

        kw = []
        for k in km.kvesty:
            stavy, tagy = [], set()
            for idx in (0, 1):
                postup, stav = km.stav(idx, k)
                if stav == "drive":
                    stavy.append("✓")
                elif stav == "ted":
                    stavy.append("★")
                    tagy.add("ted")
                elif k.je_na_konci_hry():
                    stavy.append("–")
                else:
                    stavy.append(f"{postup}/{k.pocet}")
            tag = "ted" if "ted" in tagy else ("drive" if all(s == "✓" for s in stavy) else "")
            popis = f"{k.popis}  ({k.body} bodů)   ✓ = splněno dříve, ★ = splněno v této partii"
            kw.append((k.id, k.nazev, stavy[0], stavy[1], tag, popis))
        self.view.nastav_kwesty(kw)
        self.view.rezim_konec(gm.je_konec())
