"""
MapaWidget

Componente reutilizable para integrar el render del JSON en la ventana principal.
Este widget usa tkinter (Frame) y las funciones auxiliares del script
`render_constelaciones.py` (que está en la raíz del proyecto) para cargar y dibujar
las constelaciones.

API breve:
- MapaWidget(master, width=800, height=800)
- load(path) -> carga el JSON y redibuja
- clear() -> limpia el canvas

Este archivo proporciona una implementación mínima lista para importar desde
`views/main_window.py` o desde cualquier controlador GUI que uses.
"""

import os
import tkinter as tk
from typing import Optional

# Importamos las funciones auxiliares del script de renderizado existente.
import sys
# Asegurar que la raíz del proyecto está en sys.path para que la importación
# de `render_constelaciones` funcione aunque el usuario ejecute este archivo
# directamente desde cualquier directorio.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
	sys.path.insert(0, project_root)

try:
	from .... import render_constelaciones as rc
except Exception:
	# Si la importación relativa falla (por estructura de paquetes), intentamos importación directa
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

	def clear(self):
		self.canvas.delete("all")
		self.data = None

	def load(self, path: Optional[str] = None):
		"""Carga el JSON desde `path`. Si no se pasa, busca `constelaciones.json` al lado del script principal."""
		if path is None:
			default = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'constelaciones.json')
			path = os.path.abspath(default)
		if rc is None:
			raise RuntimeError("No se pudo importar el módulo de render (render_constelaciones). Asegúrate de que existe en la raíz del proyecto.")
		self.data = rc.load_json(path)
		self.draw()

	def draw(self):
		"""Dibuja el contenido de `self.data` en el canvas usando las utilidades del renderizador."""
		self.clear()
		if not self.data:
			return
		# Usamos las mismas funciones que el script para coherencia
		minx, miny, width, height = rc.compute_bounds(self.data)
		counts = rc.collect_coords_counts(self.data)
		cons = self.data.get("constellations", [])
		colors = rc.generate_colors(len(cons))

		for ci, c in enumerate(cons):
			color = colors[ci]
			for s in c.get("starts", []):
				x1 = s["coordenates"]["x"]
				y1 = s["coordenates"]["y"]
				for link in s.get("linkedTo", []):
					other = rc.find_star_by_id(self.data, link["starId"])
					if not other:
						continue
					x2 = other["coordenates"]["x"]
					y2 = other["coordenates"]["y"]
					cx1, cy1 = rc.coord_to_canvas(x1, y1, minx, miny, width, height)
					cx2, cy2 = rc.coord_to_canvas(x2, y2, minx, miny, width, height)
					self.canvas.create_line(cx1, cy1, cx2, cy2, fill=color, width=2, tags="edge")
			for s in c.get("starts", []):
				x = s["coordenates"]["x"]
				y = s["coordenates"]["y"]
				cx, cy = rc.coord_to_canvas(x, y, minx, miny, width, height)
				r = max(3, s.get("radius", 0.5) * 6)
				coord_key = (x, y)
				star_color = "red" if counts.get(coord_key, 0) > 1 else color
				if s.get("hypergiant"):
					self.canvas.create_oval(cx-r-3, cy-r-3, cx+r+3, cy+r+3, outline="yellow", width=2)
				self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=star_color, outline="white")
				lbl = s.get("label", str(s.get("id")))
				self.canvas.create_text(cx, cy - r - 8, text=lbl, fill="white", font=("Arial", 9))

		# leyenda simple
		for i, c in enumerate(cons):
			x = 10
			y = 10 + i*18
			self.canvas.create_rectangle(x, y, x+14, y+14, fill=colors[i], outline="")
			self.canvas.create_text(x+20, y+7, anchor="w", text=c.get("name",""), fill="white", font=("Arial", 10))


if __name__ == "__main__":
	# pequeña prueba manual si se ejecuta directamente
	root = tk.Tk()
	root.title("MapaWidget - prueba")
	widget = MapaWidget(root)
	widget.pack(fill="both", expand=True)
	try:
		widget.load()
	except Exception as e:
		print("Error carga por defecto:", e)
	root.mainloop()
