import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from model.definice_figurek import RegistrFigurek
from model.kwest_manager import KwestKatalog
from model.user_manager import UserManager
from view import theme
from view.dialogs import NovaHraDialog
from view.figurka_editor import FigurkaEditor
from view.hraci_view import HraciView
from view.kwest_editor import KwestEditor
from view.menu_view import MenuView

DATA = Path(__file__).resolve().parent.parent / "data"


class AppController:
    """Hlavní controller: drží okno, data a přepíná obrazovky."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ChessWithQuests")
        self.root.geometry("1220x820")
        self.root.minsize(920, 640)
        theme.aplikuj(self.root)
        self.registr = RegistrFigurek(DATA / "figurky.json")
        self.katalog = KwestKatalog(DATA / "kwesty.json")
        self.users = UserManager(DATA / "uzivatele.json")
        self.obrazovka: tk.Widget | None = None
        self.hra = None                       # GameController běžící partie
        self.posledni_nastaveni: dict | None = None
        self.root.protocol("WM_DELETE_WINDOW", self.konec)

    def zobraz(self, frame: tk.Widget):
        if self.obrazovka is not None:
            self.obrazovka.destroy()
        self.obrazovka = frame
        frame.pack(fill="both", expand=True)

    def zobraz_menu(self):
        self.hra = None
        self.zobraz(MenuView(self.root, self))

    def nova_hra(self):
        cfg = NovaHraDialog(self.root, self.registr, self.users.jmena(), self.posledni_nastaveni).ukaz()
        if cfg:
            self.spust_hru(cfg)

    def spust_hru(self, cfg: dict):
        from controller.game_controller import GameController
        self.posledni_nastaveni = cfg
        self.hra = GameController(self, cfg)

    def editor_figurek(self):
        FigurkaEditor(self.root, self.registr).ukaz()

    def editor_kwestu(self):
        KwestEditor(self.root, self.katalog, self.registr).ukaz()

    def hraci(self):
        HraciView(self.root, self.users, self.katalog).ukaz()

    def konec(self):
        if self.hra is not None:
            if not self.hra.gm.je_konec() and not messagebox.askyesno(
                    "Ukončit", "Partie ještě běží. Opravdu ukončit hru?\n(Splněné kwesty se uloží.)",
                    parent=self.root):
                return
            self.hra.ukonci()
        self.root.destroy()

    def spust(self):
        self.zobraz_menu()
        self.root.mainloop()
