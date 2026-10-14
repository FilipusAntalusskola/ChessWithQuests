"""Barvy, písma a kreslení figurek – společné pro celé GUI."""
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

# Paleta "stará mapa / dřevěná deska"
B = {
    "pozadi": "#231C17",
    "panel": "#2E251F",
    "panel2": "#3A2F27",
    "okraj": "#4A3C31",
    "text": "#F1E6D0",
    "tlumeny": "#B5A387",
    "akcent": "#D9A441",
    "akcent_tmavy": "#9C7425",
    "svetle_pole": "#EBD9B4",
    "tmave_pole": "#A5734A",
    "posledni_svetle": "#E3CC77",
    "posledni_tmave": "#B89144",
    "vyber": "#F2C94C",
    "tecka": "#3F5E47",
    "sach": "#C2412D",
    "bila": "#FBF6EA",
    "cerna": "#1C1612",
    "chyba": "#E07A5F",
}

GLYF = {'K': '\u265A', 'D': '\u265B', 'V': '\u265C', 'S': '\u265D', 'J': '\u265E', 'P': '\u265F'}
OBRYS = {'K': '\u2654', 'D': '\u2655', 'V': '\u2656', 'S': '\u2657', 'J': '\u2658', 'P': '\u2659'}

NADPIS = ("Georgia", 30, "bold")
PODNADPIS = ("Georgia", 13, "italic")
H2 = ("Georgia", 15, "bold")
TEXT = ("Segoe UI", 10)
TEXT_B = ("Segoe UI", 10, "bold")
MALY = ("Segoe UI", 9)
HODINY = ("Consolas", 18, "bold")

_font_figurek = None


def font_figurek(root) -> str:
    """Najde písmo, které umí šachové symboly."""
    global _font_figurek
    if _font_figurek is None:
        dostupne = set(tkfont.families(root))
        for kandidat in ("Segoe UI Symbol", "DejaVu Sans", "Noto Sans Symbols2", "Arial Unicode MS",
                         "FreeSerif", "Symbola", "Apple Symbols"):
            if kandidat in dostupne:
                _font_figurek = kandidat
                break
        else:
            _font_figurek = "TkDefaultFont"
    return _font_figurek


def aplikuj(root: tk.Tk):
    root.configure(bg=B["pozadi"])
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(".", background=B["panel"], foreground=B["text"], fieldbackground=B["panel2"],
                    bordercolor=B["okraj"], lightcolor=B["panel2"], darkcolor=B["panel"], font=TEXT)
    style.configure("TNotebook", background=B["panel"], borderwidth=0)
    style.configure("TNotebook.Tab", background=B["panel2"], foreground=B["tlumeny"], padding=(12, 5))
    style.map("TNotebook.Tab", background=[("selected", B["okraj"])], foreground=[("selected", B["text"])])
    style.configure("Treeview", background=B["panel2"], fieldbackground=B["panel2"], foreground=B["text"],
                    rowheight=24, borderwidth=0)
    style.configure("Treeview.Heading", background=B["okraj"], foreground=B["text"], font=TEXT_B)
    style.map("Treeview", background=[("selected", B["akcent_tmavy"])])
    style.configure("TCombobox", fieldbackground=B["panel2"], background=B["okraj"], foreground=B["text"],
                    arrowcolor=B["text"])
    style.map("TCombobox", fieldbackground=[("readonly", B["panel2"])], foreground=[("readonly", B["text"])])
    style.configure("TSpinbox", fieldbackground=B["panel2"], background=B["okraj"], foreground=B["text"],
                    arrowcolor=B["text"])
    style.configure("TCheckbutton", background=B["panel"], foreground=B["text"])
    style.map("TCheckbutton", background=[("active", B["panel"])])
    style.configure("Vertical.TScrollbar", background=B["okraj"], troughcolor=B["panel"], arrowcolor=B["text"])
    root.option_add("*TCombobox*Listbox.background", B["panel2"])
    root.option_add("*TCombobox*Listbox.foreground", B["text"])


def tlacitko(master, text, prikaz, hlavni=False, **kw):
    """Ploché tlačítko v barvách aplikace."""
    bg = B["akcent"] if hlavni else B["panel2"]
    fg = B["cerna"] if hlavni else B["text"]
    aktivni = "#E8B85A" if hlavni else B["okraj"]
    b = tk.Button(master, text=text, command=prikaz, bg=bg, fg=fg, activebackground=aktivni,
                  activeforeground=fg, relief="flat", bd=0, padx=14, pady=7, cursor="hand2",
                  font=TEXT_B if hlavni else TEXT, highlightthickness=0, **kw)
    return b


def stitek(master, text="", font=TEXT, fg=None, bg=None, **kw):
    return tk.Label(master, text=text, font=font, fg=fg or B["text"], bg=bg or B["panel"], **kw)


def vstup(master, **kw):
    return tk.Entry(master, bg=B["panel2"], fg=B["text"], insertbackground=B["text"], relief="flat",
                    highlightthickness=1, highlightbackground=B["okraj"], highlightcolor=B["akcent"],
                    font=TEXT, **kw)


def textove_pole(master, **kw):
    return tk.Text(master, bg=B["panel2"], fg=B["text"], insertbackground=B["text"], relief="flat",
                   highlightthickness=1, highlightbackground=B["okraj"], highlightcolor=B["akcent"],
                   font=("Consolas", 10), wrap="none", **kw)


def nakresli_figurku(canvas: tk.Canvas, fig, cx: float, cy: float, velikost: float, tag="fig"):
    """Nakreslí figurku na plátno. Vestavěné figurky jako šachové symboly,
    vlastní figurky jako kotouč se značkou (nebo vlastním symbolem)."""
    bila = fig.getBarvu() == 1
    znacka = fig.getZnacku()
    rodina = font_figurek(canvas.winfo_toplevel())
    if znacka in GLYF and not fig.symbol:
        f = (rodina, -int(velikost * 0.80))
        if bila:
            canvas.create_text(cx, cy + velikost * 0.02, text=GLYF[znacka], font=f, fill=B["bila"], tags=tag)
            canvas.create_text(cx, cy + velikost * 0.02, text=OBRYS[znacka], font=f, fill=B["cerna"], tags=tag)
        else:
            canvas.create_text(cx, cy + velikost * 0.02, text=GLYF[znacka], font=f, fill=B["cerna"], tags=tag)
        return
    r = velikost * 0.36
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=B["bila"] if bila else B["cerna"],
                       outline=B["cerna"] if bila else B["akcent"], width=max(1, velikost * 0.05), tags=tag)
    canvas.create_oval(cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78,
                       outline=B["akcent_tmavy"], width=1, tags=tag)
    znak = fig.symbol or znacka
    canvas.create_text(cx, cy, text=znak, fill=B["cerna"] if bila else B["bila"],
                       font=(rodina if fig.symbol else "Georgia", -int(velikost * 0.40), "bold"), tags=tag)


def smichej(c1: str, c2: str, t: float) -> str:
    """Smíchá dvě barvy #rrggbb v poměru t (0 = c1, 1 = c2)."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))
