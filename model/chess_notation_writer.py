import io

from model.chess_notation_formatter import ChessNotationFormatter
from model.tah import Tah


class ChessNotationWriter:
    # Zapíše průběh partie (posloupnost tahů)

    def __init__(self, out: io.TextIOBase, formatter: ChessNotationFormatter | None = None):
        self.out = out
        self.formatter = formatter or ChessNotationFormatter()

    def print(self, tahy: list[tuple[Tah | None, Tah | None]], vysledek: str | None = None) -> int:
        count = 0
        linelen = 0
        for i, (t0, t1) in enumerate(tahy):
            s0 = ".." if t0 is None else " " + self.formatter.toStr(t0)
            s1 = "" if t1 is None else " " + self.formatter.toStr(t1)
            s = f"{i + 1}.{s0}{s1} "
            if linelen + len(s) > 80:
                print(file=self.out)
                linelen = 0
            print(s, file=self.out, end='')
            linelen += len(s)
            count += 1
        if vysledek:
            print(vysledek, file=self.out, end='')
        print(file=self.out)
        return count
