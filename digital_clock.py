"""
Neon Digital Clock  -  Python + Tkinter (no extra packages needed)

Controls
    T      switch theme
    F      toggle 12h / 24h
    F11    fullscreen on/off
    Esc    quit
"""
import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime

THEMES = [
    {   # electric cyan on midnight blue
        "name": "Neon Night",
        "bg": "#0a0e1a", "panel": "#111830", "fg": "#00f5d4",
        "glow": "#00675b", "accent": "#f15bb5", "dim": "#1e2a4a", "text": "#8892b0",
    },
    {   # warm gradient feel
        "name": "Sunset Glow",
        "bg": "#1a0f1f", "panel": "#2a1630", "fg": "#ffb347",
        "glow": "#7a3d12", "accent": "#ff5e78", "dim": "#3b2342", "text": "#c9a3b5",
    },
    {   # classic terminal
        "name": "Matrix",
        "bg": "#020a04", "panel": "#06170a", "fg": "#39ff14",
        "glow": "#116b05", "accent": "#b6ff9e", "dim": "#0d2a12", "text": "#4f9a5a",
    },
    {   # clean light theme
        "name": "Paper Mono",
        "bg": "#f4f1ea", "panel": "#e7e2d6", "fg": "#222222",
        "glow": "#cfc9ba", "accent": "#d9482b", "dim": "#d5cfbf", "text": "#6b665a",
    },
]


class DigitalClock(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Digital Clock")
        self.geometry("900x520")
        self.minsize(520, 320)

        self.theme_i = 0
        self.use_24h = True
        self.fullscreen = False

        families = set(tkfont.families())
        self.family = next(
            (f for f in ("Orbitron", "Consolas", "SF Mono", "Menlo",
                         "DejaVu Sans Mono", "Courier New") if f in families),
            "Courier",
        )

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.bind("<Key-t>", lambda e: self.next_theme())
        self.bind("<Key-T>", lambda e: self.next_theme())
        self.bind("<Key-f>", lambda e: self.toggle_format())
        self.bind("<Key-F>", lambda e: self.toggle_format())
        self.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.bind("<Escape>", lambda e: self.destroy())
        self.canvas.bind("<Button-1>", lambda e: self.next_theme())  # click = new theme

        self.tick()

    # ---- controls -------------------------------------------------------
    def next_theme(self):
        self.theme_i = (self.theme_i + 1) % len(THEMES)

    def toggle_format(self):
        self.use_24h = not self.use_24h

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    # ---- drawing --------------------------------------------------------
    def glow_text(self, x, y, text, font, fg, glow):
        """Fake a neon glow by stamping a dim copy around the main text."""
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3),
                       (-2, -2), (2, -2), (-2, 2), (2, 2)):
            self.canvas.create_text(x + dx, y + dy, text=text, font=font, fill=glow)
        self.canvas.create_text(x, y, text=text, font=font, fill=fg)

    def draw(self, now):
        t = THEMES[self.theme_i]
        c = self.canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        c.configure(bg=t["bg"])

        # rounded-ish card behind everything
        pad = min(w, h) * 0.06
        c.create_rectangle(pad, pad, w - pad, h - pad,
                           fill=t["panel"], outline=t["dim"], width=2)

        # time string (colons blink every second)
        fmt = "%H:%M:%S" if self.use_24h else "%I:%M:%S"
        s = now.strftime(fmt)
        if now.microsecond > 500_000:
            s = s.replace(":", " ")
        size = int(min(w / 6.4, h / 3.2))
        big = (self.family, size, "bold")
        self.glow_text(w / 2, h * 0.42, s, big, t["fg"], t["glow"])

        # AM / PM tag
        if not self.use_24h:
            c.create_text(w / 2 + size * 3.1, h * 0.42 - size * 0.55,
                          text=now.strftime("%p"),
                          font=(self.family, max(12, size // 4), "bold"),
                          fill=t["accent"])

        # date
        c.create_text(w / 2, h * 0.64, text=now.strftime("%A, %d %B %Y").upper(),
                      font=(self.family, max(11, size // 4)), fill=t["text"])

        # seconds progress bar
        bw, bh = w * 0.6, max(6, h * 0.018)
        x0, y0 = (w - bw) / 2, h * 0.74
        c.create_rectangle(x0, y0, x0 + bw, y0 + bh, fill=t["dim"], outline="")
        frac = (now.second + now.microsecond / 1e6) / 60
        c.create_rectangle(x0, y0, x0 + bw * frac, y0 + bh, fill=t["accent"], outline="")

        # footer
        c.create_text(pad + 14, pad + 14, anchor="nw", text=t["name"].upper(),
                      font=(self.family, 10, "bold"), fill=t["accent"])
        c.create_text(w / 2, h - pad - 16,
                      text="T / click: theme   F: 12h-24h   F11: fullscreen   Esc: quit",
                      font=(self.family, 9), fill=t["text"])

    def tick(self):
        self.draw(datetime.now())
        self.after(100, self.tick)


if __name__ == "__main__":
    DigitalClock().mainloop()
