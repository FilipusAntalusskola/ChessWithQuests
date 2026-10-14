import copy
import datetime
from dataclasses import dataclass, field

from model.export_writer import ExportWriter
from model.chess_notation_writer import ChessNotationWriter
from model.chess_notation_formatter import ChessNotationFormatter_Pgn
from model.figurka import Pesak
from model.game_logger import GameLogger
from model.game_timer import GameTimer
from model.herni_plocha import Herni_Plocha
from model.hrac import Hrac
from model.kwest import Kwest
from model.kwest_manager import KwestManager
from model.metadata_writer import MetadataWriter_Pgn
from model.pol import Pol
from model.revizor_tahu import RevizorTahu
from model.tah import Tah

# Stavy partie
HRAJE, MAT, PAT, VZDANO, REMIZA, CAS = range(6)
POPIS_STAVU = {HRAJE: "hraje se", MAT: "mat", PAT: "pat", VZDANO: "vzdáno", REMIZA: "remíza dohodou",
               CAS: "vypršel čas"}


@dataclass
class VysledekTahu:
    tah: Tah
    nove_kwesty: list[tuple[int, Kwest]] = field(default_factory=list)
    konec: bool = False


class GameManager:
    """Řídí jednu partii dvou hráčů na jednom počítači (model – nic neví o GUI)."""

    def __init__(self, plocha: Herni_Plocha, hraci: list[Hrac], kwest_manager: KwestManager | None = None,
                 casovac: GameTimer | None = None, game_logger: GameLogger | None = None, registr=None):
        self.plocha = plocha
        self.hraci = hraci                  # [0] = bílý, [1] = černý
        self.aktivni_hrac = 0               # index do self.hraci
        self.aktualni_tah: Tah | None = None
        self.casovac = casovac or GameTimer()
        self.game_logger = game_logger or GameLogger()
        self.kwest_manager = kwest_manager or KwestManager()
        self.registr = registr
        self.stav = HRAJE
        self.vitez: int | None = None
        self.pocet_tahu = [0, 0]
        self.historie: list = []            # snímky stavu pro "tah zpět"
        self.casovac.nuluj_cas(0)

    def __str__(self):
        return f"GameManager – na tahu: {self.hraci[self.aktivni_hrac]}"

    # ------------------------------------------------------------ dotazy
    def aktivni_barva(self) -> int:
        return self.hraci[self.aktivni_hrac].getBarvu()

    def get_stav(self) -> int:
        return self.stav

    def je_konec(self) -> bool:
        return self.stav != HRAJE

    def posledni_tah(self) -> Tah | None:
        return self.plocha.getPredTah()

    def je_sach(self) -> Pol | None:
        # Pole krále na tahu, pokud je v šachu
        barva = self.aktivni_barva()
        if self.plocha.check_sach(barva) == barva:
            return self.plocha.najdi_krale(barva)
        return None

    def mozni_tahy(self) -> list[Tah]:
        return self.plocha.getAllLegalMoves(self.aktivni_barva())

    def mozne_tahy_z(self, start: Pol) -> list[Tah]:
        if self.je_konec():
            return []
        fig = self.plocha.vrat_obsah(start)
        if fig is None or fig.getBarvu() != self.aktivni_barva():
            return []
        return self.plocha.getLegalMovesFrom(start)

    def vyzaduje_promenu(self, start: Pol, cil: Pol) -> bool:
        fig = self.plocha.vrat_obsah(start)
        if not isinstance(fig, Pesak):
            return False
        return RevizorTahu(self.plocha, None).je_posledni_rada(cil, fig.getBarvu())

    # ------------------------------------------------------------ tahy
    def _rozliseni(self, start: Pol, cil: Pol) -> str:
        # Pro notaci: pokud může na cíl táhnout i jiná stejná figurka, přidáme sloupec/řadu.
        fig = self.plocha.vrat_obsah(start)
        if fig is None or isinstance(fig, Pesak):
            return ""
        jine = []
        for pol, f in self.plocha.figurky(fig.getBarvu()):
            if pol != start and f.getZnacku() == fig.getZnacku():
                rev = RevizorTahu(self.plocha, Tah(pol, cil, f))
                if rev.precheckmove() and rev.simulate_move():
                    jine.append(pol)
        if not jine:
            return ""
        if all(p.getSloupec() != start.getSloupec() for p in jine):
            return str(start)[0]
        if all(p.getRad() != start.getRad() for p in jine):
            return str(start.getRad())
        return str(start)

    def _snimek(self):
        return (copy.deepcopy((self.plocha, self.game_logger.tahy, self.pocet_tahu)),
                self.kwest_manager.uloz_stav(), self.aktivni_hrac)

    def proved_tah(self, start: Pol, cil: Pol, nahrad_znacka: str | None = None) -> VysledekTahu | None:
        """Provede tah hráče na tahu. Vrátí None, pokud tah není platný
        (nebo chybí volba figurky při proměně pěšce)."""
        if self.je_konec():
            return None
        fig = self.plocha.vrat_obsah(start)
        if fig is None or fig.getBarvu() != self.aktivni_barva():
            return None
        nahrad = None
        if self.vyzaduje_promenu(start, cil):
            if not nahrad_znacka:
                return None
            if self.registr is not None:
                nahrad = self.registr.vytvor(nahrad_znacka, fig.getBarvu())
            else:
                from model.figurka import VESTAVENE_TRIDY
                nahrad = VESTAVENE_TRIDY[nahrad_znacka](fig.getBarvu())

        rozliseni = self._rozliseni(start, cil)
        snimek = self._snimek()
        tah = self.plocha.createTah(start, cil, nahrad)
        if tah is None or not RevizorTahu(self.plocha, tah).proved_tah():
            return None

        self.historie.append(snimek)
        tah.rozliseni = rozliseni
        self.aktualni_tah = tah
        self.game_logger.addTah(tah)
        hrac = self.aktivni_hrac
        self.pocet_tahu[hrac] += 1

        udalost = {
            "kym": fig.getZnacku(),
            "koho": tah.capture.getZnacku() if tah.capture is not None else None,
            "sach": tah.sach, "mat": tah.mat,
            "rosada": bool(tah.rosada), "en_passant": tah.enPassant,
            "promena": nahrad.getZnacku() if nahrad is not None else None,
        }
        vysledek = VysledekTahu(tah, [(hrac, k) for k in self.kwest_manager.zpracuj_tah(hrac, udalost)])

        if tah.mat:
            vysledek.nove_kwesty += self._ukonci(MAT, hrac)
        elif tah.pat:
            vysledek.nove_kwesty += self._ukonci(PAT, None)
        else:
            self.aktivni_hrac = 1 - self.aktivni_hrac
            self.casovac.switch()
        vysledek.konec = self.je_konec()
        return vysledek

    def zrus_tah(self) -> bool:
        """Vrátí poslední tah. Po skončení partie už nejde."""
        if not self.historie or self.je_konec():
            return False
        data, kwest_stav, aktivni = self.historie.pop()
        self.plocha, self.game_logger.tahy, self.pocet_tahu = data
        self.kwest_manager.obnov_stav(kwest_stav)
        self.aktivni_hrac = aktivni
        self.aktualni_tah = None
        self.casovac.pokracuj(aktivni)
        return True

    # ------------------------------------------------------------ konec partie
    def _ukonci(self, stav: int, vitez: int | None) -> list[tuple[int, Kwest]]:
        self.stav = stav
        self.vitez = vitez
        self.casovac.stop()
        return self.kwest_manager.zpracuj_konec(vitez, self.pocet_tahu)

    def vzdat(self, hrac: int) -> list[tuple[int, Kwest]]:
        if self.je_konec():
            return []
        return self._ukonci(VZDANO, 1 - hrac)

    def remiza(self) -> list[tuple[int, Kwest]]:
        if self.je_konec():
            return []
        return self._ukonci(REMIZA, None)

    def kontrola_casu(self) -> list[tuple[int, Kwest]] | None:
        # Vrátí seznam nových kwestů, pokud hráči na tahu právě vypršel čas; jinak None.
        if self.je_konec() or not self.casovac.vyprsel(self.aktivni_hrac):
            return None
        return self._ukonci(CAS, 1 - self.aktivni_hrac)

    def skore_bileho(self) -> float:
        if self.vitez is None:
            return 0.5
        return 1.0 if self.vitez == 0 else 0.0

    def vysledek_pgn(self) -> str:
        if not self.je_konec():
            return "*"
        return {1.0: "1-0", 0.0: "0-1", 0.5: "1/2-1/2"}[self.skore_bileho()]

    # ------------------------------------------------------------ export
    def export_pgn(self, out, rada: str = "") -> int:
        meta = {
            "Event": "ChessWithQuests – lokální partie",
            "Site": "Lokální multiplayer",
            "Date": datetime.date.today().strftime("%Y.%m.%d"),
            "Round": "1",
            "White": self.hraci[0].getJmeno(),
            "Black": self.hraci[1].getJmeno(),
            "Result": self.vysledek_pgn(),
            "PlyCount": str(self.game_logger.pocet_pultahu()),
            "Board": f"{self.plocha.rozmery[0]}x{self.plocha.rozmery[1]}",
        }
        if self.je_konec():
            meta["Termination"] = POPIS_STAVU[self.stav]
        if rada:
            meta["Variant"] = rada
        writer = ExportWriter(out, ChessNotationWriter(out, ChessNotationFormatter_Pgn()), MetadataWriter_Pgn(out))
        return writer.print(self.game_logger.getTahy(), meta)

    # ------------------------------------------------------------ z verze (4)
    def najdi_uzivatele(self, jmeno: str):
        for hrac in self.hraci:
            if hrac.uzivatel.uzivatelske_jmeno == jmeno:
                return hrac.uzivatel
        return None
