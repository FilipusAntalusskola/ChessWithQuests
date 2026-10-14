"""Formátovače šachové notace (převzato z projektu (3) a opraveno)."""
from model.figurka import Figurka, Pesak
from model.tah import Tah


class ChessNotationFormatter:
    # Základní formátovač – vypíše tah tak, jak ho vypíše str(tah)
    cz2code = {'K': 'K', 'D': 'Q', 'S': 'B', 'J': 'N', 'V': 'R', 'P': ''}

    def getFigureCode(self, fig: Figurka | None) -> str:
        if fig is None:
            return '?'
        # Vlastní (definované) figurky nemají standardní kód – použije se jejich značka
        return self.cz2code.get(fig.getZnacku(), fig.getZnacku())

    def toStr(self, tah: Tah | None) -> str:
        return "<None>" if tah is None else str(tah)


class ChessNotationFormatter_San(ChessNotationFormatter):
    # Krátká algebraická notace (anglické značky: Nf3, exd5, O-O, e8Q+)
    rosady = {1: '0–0', 2: '0–0–0'}

    def _promena(self, tah: Tah) -> str:
        return self.getFigureCode(tah.nahrad) if tah.nahrad else ''

    def toStr(self, tah: Tah | None) -> str:
        if tah is None:
            return "<None>"
        if tah.rosada:
            res = self.rosady[tah.rosada]
        else:
            fig = tah.getFigurku()
            if isinstance(fig, Pesak):
                res = '' if tah.capture is None else str(tah.getStart())[0]
            else:
                res = self.getFigureCode(fig) + getattr(tah, 'rozliseni', '')
            if tah.capture is not None:
                res += 'x'
            res += str(tah.getCil())
            res += self._promena(tah)
            if tah.enPassant:
                res += ' e.p.'
        if tah.mat:
            res += '#'
        elif tah.sach:
            res += '+'
        return res


class ChessNotationFormatter_SanCz(ChessNotationFormatter_San):
    # Krátká notace s českými značkami (Jf3, Sb5, Dxd8) – používá GUI
    def getFigureCode(self, fig: Figurka | None) -> str:
        if fig is None:
            return '?'
        return '' if isinstance(fig, Pesak) else fig.getZnacku()


class ChessNotationFormatter_Lan(ChessNotationFormatter):
    # Dlouhá algebraická notace (Ng1–f3, e2–e4)
    def toStr(self, tah: Tah | None) -> str:
        if tah is None:
            return "<None>"
        if tah.rosada:
            res = '0–0' if tah.rosada == 1 else '0–0–0'
        else:
            res = self.getFigureCode(tah.getFigurku())
            res += str(tah.getStart())
            res += '–' if tah.capture is None else 'x'
            res += str(tah.getCil())
            if tah.nahrad:
                res += self.getFigureCode(tah.nahrad)
            if tah.enPassant:
                res += ' e.p.'
        if tah.mat:
            res += '#'
        elif tah.sach:
            res += '+'
        return res


class ChessNotationFormatter_Fan(ChessNotationFormatter_San):
    # Figurková notace (♘f3)
    symboly = {'K': ('\u2654', '\u265A'), 'D': ('\u2655', '\u265B'), 'S': ('\u2657', '\u265D'),
               'J': ('\u2658', '\u265E'), 'V': ('\u2656', '\u265C'), 'P': ('', '')}

    def getFigureCode(self, fig: Figurka | None) -> str:
        if fig is None:
            return '?'
        if fig.getZnacku() not in self.symboly:
            return fig.getZnacku()
        return self.symboly[fig.getZnacku()][(1 - fig.getBarvu()) // 2]


class ChessNotationFormatter_Pgn(ChessNotationFormatter_San):
    # Notace pro soubory PGN (O-O, e8=Q)
    rosady = {1: 'O-O', 2: 'O-O-O'}

    def _promena(self, tah: Tah) -> str:
        return '=' + self.getFigureCode(tah.nahrad) if tah.nahrad else ''

    def toStr(self, tah: Tah | None) -> str:
        return super().toStr(tah).replace(' e.p.', '')
