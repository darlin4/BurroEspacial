# components/mapa_widget.py
import tkinter as tk
from tkinter import messagebox

class MapaWidget(tk.Frame):
    """Frame que contiene el canvas para dibujar el mapa estelar."""

    def __init__(self, master=None, width=800, height=800, **kwargs):
        super().__init__(master, **kwargs)
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="black")
        self.canvas.pack(fill="both", expand=True)
        self.data = None

    def clear(self):
        self.canvas.delete("all")
        self.data = None

    def load(self, data):
        """Carga los datos del JSON y dibuja las constelaciones."""
        if not data or "constellations" not in data:
            messagebox.showinfo("Aviso", "El JSON no contiene constelaciones para dibujar.")
            return

        self.data = data
        const_data = data["constellations"]
        if not const_data:
            messagebox.showinfo("Aviso", "No hay constelaciones dentro del JSON.")
            return

        self.canvas.delete("all")

        # obtener rangos para escalar
        all_x = [s["coordenates"]["x"] for c in const_data for s in c.get("starts", [])]
        all_y = [s["coordenates"]["y"] for c in const_data for s in c.get("starts", [])]
        if not all_x or not all_y:
            return

        minx, maxx = min(all_x), max(all_x)
        miny, maxy = min(all_y), max(all_y)
        range_x = maxx - minx or 1
        range_y = maxy - miny or 1

        def to_canvas(x, y):
            cx = ((x - minx) / range_x) * (self.width - 60) + 30
            cy = ((y - miny) / range_y) * (self.height - 60) + 30
            return cx, cy

        colors = ["cyan", "orange", "magenta", "lime", "white", "pink"]

        for ci, c in enumerate(const_data):
            color = colors[ci % len(colors)]

            # conexiones
            for s in c.get("starts", []):
                x1, y1 = to_canvas(s["coordenates"]["x"], s["coordenates"]["y"])
                for link in s.get("linkedTo", []):
                    # buscar estrella con starId
                    other = None
                    for cc in const_data:
                        for st in cc.get("starts", []):
                            if st["id"] == link["starId"]:
                                other = st
                                break
                    if other:
                        x2, y2 = to_canvas(other["coordenates"]["x"], other["coordenates"]["y"])
                        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

            # estrellas
            for s in c.get("starts", []):
                x, y = to_canvas(s["coordenates"]["x"], s["coordenates"]["y"])
                r = max(3, s.get("radius", 1) * 4)
                fill = "yellow" if s.get("hypergiant") else color
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline="white")
                self.canvas.create_text(x, y - r - 8, text=s.get("label", s["id"]), fill="white", font=("Arial", 9))

        # leyenda
        for i, c in enumerate(const_data):
            self.canvas.create_text(80, 20 + i * 20, text=c.get("name", ""), fill=colors[i % len(colors)], anchor="w")
