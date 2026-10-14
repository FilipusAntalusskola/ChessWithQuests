import copy
from model.figurka import Figurka
from model.pol import Pol


class Tah:
    # Jeden (půl)tah ve hře – může být i neplatný, platnost ověřuje RevizorTahu.

    def __init__(self, vychozi_pozice: Pol, cilova_pozice: Pol, figurka: Figurka | None,
                 nahrad: Figurka | None = None):
        self.vychozi_pozice = vychozi_pozice.copy()
        self.cilova_pozice = cilova_pozice.copy()
        self.figurka = figurka
        # Následující atributy vyplní RevizorTahu po provedení tahu
        self.enPassant = False
        self.rosada = 0          # 1 = krátká (k vyššímu sloupci), 2 = dlouhá
        self.sach = False
        self.mat = False
        self.pat = False
        self.capture: Figurka | None = None    # vyhozená figurka
        self.nahrad = nahrad                    # figurka, ve kterou se pěšec mění

    def __str__(self):
        s = str(self.figurka) if self.figurka is not None else "?"
        s += str(self.vychozi_pozice) + str(self.cilova_pozice)
        if self.nahrad:
            s += str(self.nahrad)
        return s

    def copy(self):
        return copy.deepcopy(self)

    def getStart(self) -> Pol:
        return self.vychozi_pozice

    def getCil(self) -> Pol:
        return self.cilova_pozice

    def getFigurku(self) -> Figurka | None:
        return self.figurka

    def getNahradu(self) -> Figurka | None:
        return self.nahrad
