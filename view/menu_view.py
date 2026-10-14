import tkinter as tk

from view import theme
from view.theme import B, GLYF, OBRYS


class MenuView(tk.Frame):
    """Úvodní obrazovka."""

    def __init__(self, master, controller):
        super().__init__(master, bg=B["pozadi"])
        stred = tk.Frame(self, bg=B["pozadi"])
        stred.place(relx=0.5, rely=0.45, anchor="center")

        pruh = tk.Canvas(stred, width=420, height=70, bg=B["pozadi"], highlightthickness=0)
        pruh.pack()
        rodina = theme.font_figurek(self.winfo_toplevel())
        for i, z in enumerate("VJSDKSJV"):
            x = 30 + i * 51
            barva_pole = B["svetle_pole"] if i % 2 == 0 else B["tmave_pole"]
            pruh.create_rectangle(x - 25, 8, x + 25, 58, fill=barva_pole, outline="")
            pruh.create_text(x, 34, text=GLYF[z], font=(rodina, -40), fill=B["bila"] if i % 2 else B["cerna"])
            if i % 2:
                pruh.create_text(x, 34, text=OBRYS[z], font=(rodina, -40), fill=B["cerna"])

        tk.Label(stred, text="ChessWithQuests", font=theme.NADPIS, fg=B["text"], bg=B["pozadi"]).pack(pady=(14, 0))
        tk.Label(stred, text="šachy s definovatelnou deskou, figurkami a kwesty", font=theme.PODNADPIS,
                 fg=B["akcent"], bg=B["pozadi"]).pack(pady=(0, 26))

        for text, prikaz, hlavni in (("Nová partie (2 hráči)", controller.nova_hra, True),
                                     ("Editor figurek", controller.editor_figurek, False),
                                     ("Editor kwestů", controller.editor_kwestu, False),
                                     ("Hráči a žebříček", controller.hraci, False),
                                     ("Konec", controller.konec, False)):
            b = theme.tlacitko(stred, text, prikaz, hlavni=hlavni, width=26)
            b.pack(pady=4)

        tk.Label(self, text="Lokální multiplayer – oba hráči hrají na jednom počítači a střídají se u myši.",
                 font=theme.MALY, fg=B["tlumeny"], bg=B["pozadi"]).pack(side="bottom", pady=12)
