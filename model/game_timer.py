import math
import time


class GameTimer:
    # Šachové hodiny pro dva hráče (index 0 = bílý, 1 = černý).
    # limit = čas na hráče v sekundách; 0 = bez limitu (hodiny jen měří).

    def __init__(self, limit: int = 0):
        self.limit = limit
        self.cas_hrac = [0.0, 0.0]
        self.hrac: int | None = None
        self.lastswitch: float | None = None

    def __str__(self):
        return f"{self.format(0)} / {self.format(1)}"

    def nuluj_cas(self, zacina: int = 0):
        # Vynuluje a spustí hodiny pro hráče `zacina`
        self.cas_hrac = [0.0, 0.0]
        self.hrac = zacina
        self.lastswitch = time.time()
        return self

    def switch(self) -> float:
        if self.lastswitch is None:
            return 0
        now = time.time()
        self.cas_hrac[self.hrac] += now - self.lastswitch
        self.lastswitch = now
        self.hrac = 1 - self.hrac
        return self.cas_hrac[1 - self.hrac]

    def nastav_hrace(self, hrac: int):
        # Po "tahu zpět": dopočítá čas a předá hodiny hráči `hrac`
        if self.lastswitch is None:
            return
        if self.hrac != hrac:
            self.switch()

    def stop(self) -> list[float]:
        if self.lastswitch is not None:
            self.cas_hrac[self.hrac] += time.time() - self.lastswitch
            self.hrac = None
            self.lastswitch = None
        return self.cas_hrac

    def doba_trvani(self, hrac: int) -> float:
        tm = self.cas_hrac[hrac]
        if hrac == self.hrac and self.lastswitch is not None:
            tm += time.time() - self.lastswitch
        return tm

    def pokracuj(self, hrac: int):
        # Znovu spustí zastavené hodiny (např. po vrácení tahu)
        if self.lastswitch is None:
            self.hrac = hrac
            self.lastswitch = time.time()
        else:
            self.nastav_hrace(hrac)

    def zbyva(self, hrac: int) -> float | None:
        if not self.limit:
            return None
        return max(0.0, self.limit - self.doba_trvani(hrac))

    def vyprsel(self, hrac: int) -> bool:
        return bool(self.limit) and self.doba_trvani(hrac) >= self.limit

    def format(self, hrac: int) -> str:
        s = self.zbyva(hrac)
        s = int(self.doba_trvani(hrac)) if s is None else int(math.ceil(s))
        return f"{s // 60}:{s % 60:02d}"
