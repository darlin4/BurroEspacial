# components/mapa_widget.py
import os
import sys
import tkinter as tk
from tkinter import messagebox

# intentar importar utilidades de render desde la raíz del proyecto
try:
    import render_constelaciones as rc
except Exception:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    try:
        import render_constelaciones as rc
    except Exception:
        rc = None

class MapaWidget(tk.Frame):
    """Frame que contiene el canvas para dibujar el mapa estelar."""

    def __init__(self, master=None, width=800, height=800, **kwargs):
        super().__init__(master, **kwargs)
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="black")
        self.canvas.pack(fill="both", expand=True)
        self.data = None
        # grid options
        self.show_grid = True
        self.grid_spacing = 50       # pixels between grid lines
        self.label_spacing = 100     # pixels between labels (to reduce noise)

    def clear(self):
        self.canvas.delete("all")
        self.data = None

    def load(self, data_or_path):
        """Carga los datos del JSON y dibuja las constelaciones.

        data_or_path puede ser un dict (ya parseado) o una ruta (str) al JSON.
        """
        data = None
        # aceptar ruta o dict
        if isinstance(data_or_path, str):
            if rc is None:
                messagebox.showerror("Error", "No se puede importar render_constelaciones desde la raíz del proyecto.")
                return
            try:
                data = rc.load_json(data_or_path)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el JSON: {e}")
                return
        else:
            data = data_or_path

        if not data or "constellations" not in data:
            messagebox.showinfo("Aviso", "El JSON no contiene constelaciones para dibujar.")
            return

        self.data = data
        const_data = data["constellations"]
        if not const_data:
            messagebox.showinfo("Aviso", "No hay constelaciones dentro del JSON.")
            return

        self.canvas.delete("all")

        # obtener rangos para escalar (garantizar mínimo lógico 200x200)
        all_x = [s["coordenates"]["x"] for c in const_data for s in c.get("starts", [])]
        all_y = [s["coordenates"]["y"] for c in const_data for s in c.get("starts", [])]
        if not all_x or not all_y:
            return

        raw_minx, raw_maxx = min(all_x), max(all_x)
        raw_miny, raw_maxy = min(all_y), max(all_y)
        w_logical = max(200.0, raw_maxx - raw_minx or 200.0)
        h_logical = max(200.0, raw_maxy - raw_miny or 200.0)

        # usamos las utilidades de rc.coord_to_canvas si están disponibles, para mantener coherencia
        def to_canvas(x, y):
            if rc is not None:
                return rc.coord_to_canvas(x, y, raw_minx, raw_miny, w_logical, h_logical, canvas_w=self.width, canvas_h=self.height)
            # fallback simple
            cx = ((x - raw_minx) / (raw_maxx - raw_minx or 1)) * (self.width - 60) + 30
            cy = ((y - raw_miny) / (raw_maxy - raw_miny or 1)) * (self.height - 60) + 30
            return cx, cy

        colors = ["#1abc9c", "#e67e22", "#9b59b6", "#2ecc71", "#ecf0f1", "#ff69b4"]

        # dibujar una cuadrícula de 50 píxeles y etiquetas de coordenadas lógicas
        grid_size = self.grid_spacing
        grid_color = "#222222"
        label_color = "#888888"
        label_font = ("Arial", 8)
        left_margin = 30
        top_margin = 30
        usable_w = self.width - left_margin * 2
        usable_h = self.height - top_margin * 2
        # vertical lines
        for gx in range(0, int(self.width) + 1, grid_size):
            self.canvas.create_line(gx, 0, gx, self.height, fill=grid_color)
            # only label every label_spacing to reduce noise
            if (gx % self.label_spacing) == 0 and left_margin <= gx <= self.width - left_margin:
                prop = (gx - left_margin) / (usable_w or 1)
                logical_x = raw_minx + prop * (w_logical or 1)
                # pixel label
                self.canvas.create_text(gx + 2, 6, text=str(gx), fill=label_color, font=label_font, anchor="n")
                # logical coord label under the pixel label
                self.canvas.create_text(gx + 2, 18, text=f"{logical_x:.1f}", fill=label_color, font=label_font, anchor="n")
        # horizontal lines
        for gy in range(0, int(self.height) + 1, grid_size):
            self.canvas.create_line(0, gy, self.width, gy, fill=grid_color)
            if (gy % self.label_spacing) == 0 and top_margin <= gy <= self.height - top_margin:
                prop = (gy - top_margin) / (usable_h or 1)
                logical_y = raw_miny + prop * (h_logical or 1)
                # pixel label (left)
                self.canvas.create_text(4, gy + 2, text=str(gy), fill=label_color, font=label_font, anchor="w")
                # logical coord label slightly to the right
                self.canvas.create_text(36, gy + 2, text=f"{logical_y:.1f}", fill=label_color, font=label_font, anchor="w")

        # crear mapa id -> estrella y contar coordenadas
        id_map = {}
        coord_counts = {}
        for c in const_data:
            for s in c.get("starts", []):
                sid = s.get("id")
                if sid is not None:
                    id_map[sid] = s
                coord = (s["coordenates"]["x"], s["coordenates"]["y"])
                coord_counts[coord] = coord_counts.get(coord, 0) + 1

        # dibujar aristas como no dirigidas (una sola línea por par)
        drawn = set()
        missing = set()
        missing_by_source = {}
        for ci, c in enumerate(const_data):
            color = colors[ci % len(colors)]
            for s in c.get("starts", []):
                sid = s.get("id")
                x1, y1 = to_canvas(s["coordenates"]["x"], s["coordenates"]["y"])
                for link in s.get("linkedTo", []):
                    # omitir caminos bloqueados (por seguridad)
                    if link.get("blocked", False):
                        continue
                    target_id = link.get("starId")
                    tgt = id_map.get(target_id)
                    if tgt:
                        pair = tuple(sorted((sid, target_id)))
                        if pair not in drawn:
                            x2, y2 = to_canvas(tgt["coordenates"]["x"], tgt["coordenates"]["y"])
                            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
                            drawn.add(pair)
                    else:
                        missing.add(target_id)
                        if sid is not None:
                            missing_by_source.setdefault(sid, []).append(target_id)

        # dibujar estrellas y etiquetas (resaltar solapamientos en rojo)
        pos_map = {}
        for ci, c in enumerate(const_data):
            color = colors[ci % len(colors)]
            for s in c.get("starts", []):
                coord = (s['coordenates']['x'], s['coordenates']['y'])
                x, y = to_canvas(coord[0], coord[1])
                sid = s.get("id")
                pos_map[sid] = (x, y)
                r = max(3, s.get("radius", 1) * 4)
                # rojo si coord compartida por >1 estrella
                is_hyper = bool(s.get("hypergiant"))
                if coord_counts.get(coord, 0) > 1:
                    fill = "red"
                    outline = "white"
                    outline_w = 1
                else:
                    fill = color
                    outline = "yellow" if is_hyper else "white"
                    outline_w = 3 if is_hyper else 1
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline=outline, width=outline_w)
                self.canvas.create_text(x, y - r - 8, text=s.get("label", s.get("id")), fill="white", font=("Arial", 9))

        # después de dibujar, anotar en rojo junto a la estrella si tiene enlaces
        # hacia ids que faltan
        # dibujar anotación compacta para referencias faltantes (una burbuja por origen)
        # objetivo: evitar mucho ruido en el canvas agrupando IDs en una sola etiqueta
        import math
        cx_center = self.width / 2
        cy_center = self.height / 2
        margin = 8
        for src_id, targets in missing_by_source.items():
            p = pos_map.get(src_id)
            if not p:
                continue
            px, py = p
            tid_list = sorted(set(targets))
            txt = "faltan: " + ", ".join(str(t) for t in tid_list)
            # dirección hacia el centro para posicionar la burbuja fuera de la estrella
            dx = cx_center - px
            dy = cy_center - py
            norm = math.hypot(dx, dy)
            if norm == 0:
                ux, uy = 1.0, 0.0
            else:
                ux, uy = dx / norm, dy / norm
            offset_main = 48
            tx = px + ux * offset_main
            ty = py + uy * offset_main
            # clamp dentro del canvas evitando que se salga
            tx = max(margin, min(self.width - margin, tx))
            ty = max(margin, min(self.height - margin, ty))
            # línea discontinua hacia la burbuja
            self.canvas.create_line(px, py, tx, ty, fill="red", dash=(4, 4), width=1)
            # crear texto primero y obtener su bbox para dibujar fondo legible
            text_id = self.canvas.create_text(tx, ty, text=txt, fill="red", font=("Arial", 9), anchor="w")
            bbox = self.canvas.bbox(text_id)
            if bbox:
                x1, y1, x2, y2 = bbox
                pad = 4
                # rectángulo de fondo oscuro con borde rojo
                rect = self.canvas.create_rectangle(x1 - pad, y1 - pad, x2 + pad, y2 + pad, fill="black", outline="red", width=1)
                # asegurar que el texto esté por encima del rect
                self.canvas.tag_raise(text_id, rect)

        # leyenda
        for i, c in enumerate(const_data):
            self.canvas.create_text(80, 20 + i * 20, text=c.get("name", ""), fill=colors[i % len(colors)], anchor="w")

        if missing:
            messagebox.showwarning("Advertencia",
                                   f"Faltan definiciones de estrellas referenciadas: {sorted(missing)}\n"
                                   "Agrega esas estrellas al JSON o elimina sus enlaces para que las vías se dibujen.")