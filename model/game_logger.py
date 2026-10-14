from model.export_writer import ExportWriter
from model.tah import Tah


class GameLogger:
    # Sbírá tahy a metadata partie; na konci je umí zapsat přes ExportWriter.

    def __init__(self, exporter: ExportWriter | None = None):
        self.exporter = exporter
        self.tahy: list[tuple[Tah | None, Tah | None]] = []
        self.metadata: dict[str, str] = {}

    def addTah(self, pultah: Tah | None) -> Tah | None:
        # Přidá půltah, začíná bílý
        if not self.tahy or self.tahy[-1][1] is not None:
            self.tahy.append((pultah, None))
        else:
            self.tahy[-1] = (self.tahy[-1][0], pultah)
        return pultah

    def uloz_tah(self, tah: Tah):
        # jméno z verze (4)
        return self.addTah(tah)

    def getTahy(self) -> list[tuple[Tah | None, Tah | None]]:
        return self.tahy

    def pocet_pultahu(self) -> int:
        return sum((t[0] is not None) + (t[1] is not None) for t in self.tahy)

    def addMetadata(self, tagname: str, tagvalue: str) -> tuple[str, str]:
        self.metadata[tagname] = tagvalue
        return tagname, tagvalue

    def getMetadata(self) -> dict[str, str]:
        return self.metadata

    def setExportWriter(self, exporter: ExportWriter | None):
        self.exporter = exporter
        return self

    def print(self) -> int:
        if self.exporter is None:
            return 0
        return self.exporter.print(self.tahy, self.metadata)
