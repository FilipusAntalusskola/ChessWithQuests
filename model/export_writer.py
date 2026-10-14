import io

from model.chess_notation_writer import ChessNotationWriter
from model.metadata_writer import MetadataWriter
from model.tah import Tah


class ExportWriter:
    # Zapíše celou partii (metadata + tahy)

    def __init__(self, out: io.TextIOBase, movewriter: ChessNotationWriter | None = None,
                 metawriter: MetadataWriter | None = None):
        self.out = out
        self.movewriter = movewriter or ChessNotationWriter(out)
        self.metawriter = metawriter or MetadataWriter(out)

    def print(self, tahy: list[tuple[Tah | None, Tah | None]], metadata: dict[str, str] | None) -> int:
        count = 0
        if metadata:
            count = self.metawriter.print(metadata)
            print(file=self.out)
        count += self.movewriter.print(tahy, (metadata or {}).get("Result"))
        return count
