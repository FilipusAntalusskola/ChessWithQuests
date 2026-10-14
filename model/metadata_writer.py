import io


class MetadataWriter:
    # Základní zapisovač metadat partie

    def __init__(self, out: io.TextIOBase):
        self.out = out
        # Pořadí v seznamech určuje pořadí zápisu
        self.required_tag_names: list[str] = []
        self.optional_tag_names: list[str] = []
        # Pokud optional_tag_names není prázdný, ostatní tagi se tiše vynechají.

    def metadatum2str(self, key: str, val: str) -> str:
        return key + '=' + str(val)

    def print(self, metadata: dict[str, str]) -> int:
        mymetadata = dict(metadata)
        count = 0
        for key in self.required_tag_names:
            print(self.metadatum2str(key, mymetadata.pop(key, "???")), file=self.out)
            count += 1
        for key in self.optional_tag_names:
            if key in mymetadata:
                print(self.metadatum2str(key, mymetadata.pop(key)), file=self.out)
                count += 1
        if not self.optional_tag_names:
            for key, val in mymetadata.items():
                print(self.metadatum2str(key, val), file=self.out)
                count += 1
        return count


class MetadataWriter_Pgn(MetadataWriter):
    def __init__(self, out: io.TextIOBase):
        super().__init__(out)
        self.required_tag_names = ["Event", "Site", "Date", "Round", "White", "Black", "Result"]
        # (v projektu (3) se seznam jmenoval valid_tag_names a nikdy se nepoužil)
        self.optional_tag_names = ["Annotator", "PlyCount", "TimeControl", "Time", "Termination",
                                   "Mode", "FEN", "Board", "SetUp", "Variant"]

    def metadatum2str(self, key: str, val) -> str:
        if val is None:
            val = '<None>'
        val = str(val).replace("\\", r"\\").replace('"', r'\"')
        return '[' + key + ' "' + val + '"]'


MetaDataWriter = MetadataWriter          # jména z projektu (3)
MetaDataWriter_Pgn = MetadataWriter_Pgn
