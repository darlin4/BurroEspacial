import tkinter as tk
from tkinter import ttk, messagebox


class PanelControlCaminos(tk.Frame):
	"""Panel para listar y bloquear/habilitar caminos entre estrellas.

	Se trabaja directamente sobre la estructura JSON cargada en memoria.
	Requiere:
	- get_data: callable que retorne el dict de datos actual (con 'constellations').
	- on_change: callable que será invocado tras modificar bloqueos (para redibujar mapa, etc.).
	"""

	def __init__(self, master, get_data, on_change=None):
		super().__init__(master)
		self.get_data = get_data
		self.on_change = on_change
		self._rows = []  # lista de (star_obj, link_obj, origen, destino, distancia)
		self._build_ui()
		self._cargar()

	def _build_ui(self):
		style = ttk.Style()
		# Estilos generales
		style.configure("Heading.TLabel", font=("Segoe UI", 12, "bold"), foreground="#EAEAEA", background="#111")
		style.configure("Info.TLabel", foreground="#EAEAEA", background="#111")
		style.configure("Toolbar.TFrame", background="#111")
		style.configure("Blocked.TLabel", foreground="#FF6B6B", background="#111")
		style.configure("Free.TLabel", foreground="#6BFF95", background="#111")
		# Treeview oscuro legible
		style.configure("Dark.Treeview",
			background="#121212",
			fieldbackground="#121212",
			foreground="#EAEAEA",
			rowheight=22,
			bordercolor="#333333",
			borderwidth=0)
		style.configure("Dark.Treeview.Heading",
			background="#1E1E1E",
			foreground="#EAEAEA",
			font=("Segoe UI", 10, "bold"))
		style.map("Dark.Treeview",
			background=[('selected', '#2E6CBD')],
			foreground=[('selected', '#FFFFFF')])

		top = ttk.Frame(self, style="Toolbar.TFrame")
		top.pack(fill="x", padx=8, pady=(8,4))
		left_box = ttk.Frame(top, style="Toolbar.TFrame")
		left_box.pack(side="left")
		ttk.Label(left_box, text="Gestión de Caminos", style="Heading.TLabel").pack(anchor="w")
		self.stats_label = ttk.Label(left_box, text="Caminos: 0 | Bloqueados: 0 | Libres: 0", style="Info.TLabel")
		self.stats_label.pack(anchor="w", pady=(2,0))

		right_box = ttk.Frame(top, style="Toolbar.TFrame")
		right_box.pack(side="right")
		self.var_filtro = tk.StringVar()
		ttk.Entry(right_box, textvariable=self.var_filtro, width=24).pack(side="left")
		ttk.Label(right_box, text="Filtrar:", style="Info.TLabel").pack(side="left", padx=(6,6))
		self.var_filtro.trace_add('write', lambda *args: self._aplicar_filtro())
		self.var_solo_bloq = tk.BooleanVar(value=False)
		chk = ttk.Checkbutton(right_box, text="Solo bloqueados", variable=self.var_solo_bloq, command=self._aplicar_filtro)
		chk.pack(side="left", padx=(6,6))
		ttk.Button(right_box, text="Refrescar", command=self._cargar).pack(side="left", padx=(6,0))

		cols = ("origen", "destino", "dist", "estado")
		self.tree = ttk.Treeview(self, columns=cols, show="headings", height=16, style="Dark.Treeview")
		self.tree.heading("origen", text="Origen")
		self.tree.heading("destino", text="Destino")
		self.tree.heading("dist", text="Distancia")
		self.tree.heading("estado", text="Estado")
		self.tree.column("origen", width=160)
		self.tree.column("destino", width=160)
		self.tree.column("dist", width=90, anchor="center")
		self.tree.column("estado", width=100, anchor="center")
		self.tree.pack(fill="both", expand=True, padx=8, pady=6)
		self.tree.tag_configure("odd", background="#161616", foreground="#EAEAEA")
		self.tree.tag_configure("even", background="#121212", foreground="#EAEAEA")

		btns = ttk.Frame(self)
		btns.pack(fill="x", padx=8, pady=6)
		ttk.Button(btns, text="Bloquear", command=self._bloquear_sel).pack(side="left")
		ttk.Button(btns, text="Habilitar", command=self._habilitar_sel).pack(side="left", padx=6)
		self.lbl_count = ttk.Label(btns, text="0 visibles")
		self.lbl_count.pack(side="right")
		self.btn_export = ttk.Button(btns, text="Exportar bloqueos", command=self._exportar_bloqueos)
		self.btn_export.pack(side="right", padx=(0,8))

		# Detalle y doble clic para alternar
		self.lbl_info = ttk.Label(self, text="Selecciona una fila o haz doble clic para alternar bloqueo", style="Info.TLabel")
		self.lbl_info.pack(fill="x", padx=8, pady=(0,8))
		self.tree.bind("<<TreeviewSelect>>", self._on_select)
		self.tree.bind("<Double-1>", self._on_double_click)

	def _cargar(self):
		for i in self.tree.get_children():
			self.tree.delete(i)
		self._rows.clear()
		data = self.get_data() if callable(self.get_data) else None
		if not data or "constellations" not in data:
			return
		consts = data["constellations"]
		# construir índice ID->label
		id_to_label = {}
		for c in consts:
			for s in c.get("starts", []):
				id_to_label[s.get("id")] = s.get("label")

		visible = 0
		bloqueados = 0
		for c in consts:
			for s in c.get("starts", []):
				origen_label = s.get("label")
				for link in s.get("linkedTo", []):
					dest_id = link.get("starId")
					dest_label = id_to_label.get(dest_id, f"id:{dest_id}")
					dist = link.get("distance", 0)
					bloqueado = bool(link.get("blocked", False))
					self._rows.append((s, link, origen_label, dest_label, dist))
					if bloqueado:
						bloqueados += 1
					tag = "odd" if (visible % 2) else "even"
					estado_txt = "BLOQUEADO" if bloqueado else "LIBRE"
					self.tree.insert("", "end", values=(origen_label, dest_label, dist, estado_txt), tags=(tag,))
					visible += 1
		libres = visible - bloqueados
		self.lbl_count.config(text=f"{visible} visibles")
		self.stats_label.config(text=f"Caminos: {visible} | Bloqueados: {bloqueados} | Libres: {libres}")

	def _aplicar_filtro(self):
		filtro = (self.var_filtro.get() or "").strip().lower()
		for i in self.tree.get_children():
			self.tree.delete(i)
		visible = 0
		for idx, (_s, link, orig, dest, dist) in enumerate(self._rows):
			bloq = link.get('blocked', False)
			if self.var_solo_bloq.get() and not bloq:
				continue
			txt = f"{orig} {dest} {dist} {'bloqueado' if bloq else 'libre'}".lower()
			if filtro and filtro not in txt:
				continue
			tag = "odd" if (visible % 2) else "even"
			estado_txt = "BLOQUEADO" if bloq else "LIBRE"
			self.tree.insert("", "end", values=(orig, dest, dist, estado_txt), tags=(tag,))
			visible += 1
		self.lbl_count.config(text=f"{visible} visibles (filtrado)")

	def _on_select(self, event=None):
		items = self.tree.selection()
		if not items:
			self.lbl_info.config(text="Selecciona una fila o haz doble clic para alternar bloqueo")
			return
		idx = self.tree.index(items[0])
		if 0 <= idx < len(self._rows):
			_s, link, orig, dest, dist = self._rows[idx]
			bloq = "Sí" if link.get("blocked", False) else "No"
			self.lbl_info.config(text=f"{orig} -> {dest} | d={dist} | Bloqueado: {bloq}")

	def _on_double_click(self, event=None):
		items = self.tree.selection()
		if not items:
			return
		idx = self.tree.index(items[0])
		if 0 <= idx < len(self._rows):
			_s, link, *_ = self._rows[idx]
			self._cambiar_sel(not link.get("blocked", False))

	def _exportar_bloqueos(self):
		data = self.get_data() if callable(self.get_data) else None
		if not data:
			messagebox.showinfo("Info", "No hay datos para exportar")
			return
		bloqueados = []
		for c in data.get('constellations', []):
			for s in c.get('starts', []):
				for link in s.get('linkedTo', []):
					if link.get('blocked', False):
						bloqueados.append({'origen': s.get('label'), 'starId': link.get('starId'), 'distance': link.get('distance')})
		if not bloqueados:
			messagebox.showinfo("Exportar", "No hay caminos bloqueados")
			return
		# Mostrar en un diálogo simple
		win = tk.Toplevel(self)
		win.title("Caminos bloqueados")
		text = tk.Text(win, width=60, height=20)
		text.pack(fill='both', expand=True)
		for item in bloqueados:
			text.insert('end', f"{item['origen']} -> starId={item['starId']} (dist={item['distance']})\n")
		text.config(state='disabled')

	def _sel_indices(self):
		sels = self.tree.selection()
		idxs = []
		for s in sels:
			try:
				idx = self.tree.index(s)
				idxs.append(idx)
			except Exception:
				pass
		return idxs

	def _bloquear_sel(self):
		self._cambiar_sel(True)

	def _habilitar_sel(self):
		self._cambiar_sel(False)

	def _cambiar_sel(self, bloquear):
		idxs = self._sel_indices()
		if not idxs:
			messagebox.showinfo("Info", "Selecciona al menos un camino en la lista")
			return
		cambios = 0
		for idx in idxs:
			if 0 <= idx < len(self._rows):
				star_obj, link_obj, origen_label, dest_label, _dist = self._rows[idx]
				if bool(link_obj.get("blocked", False)) != bloquear:
					# Bloquear/habilitar enlace seleccionado
					link_obj["blocked"] = bool(bloquear)
					cambios += 1
					# Intentar reflejar simétricamente en el destino si existe el enlace inverso
					data = self.get_data() if callable(self.get_data) else None
					if data and "constellations" in data:
						for c in data["constellations"]:
							for s in c.get("starts", []):
								if s.get("label") == dest_label:
									for l2 in s.get("linkedTo", []):
										# l2 apunta al origen?
										target_id = l2.get("starId")
										# Resolver nombre del target
										# Construir id->label rápido
										# (para evitar recomputar fuera, resolvemos inline)
										label_target = None
										for c2 in data["constellations"]:
											for s2 in c2.get("starts", []):
												if s2.get("id") == target_id:
													label_target = s2.get("label")
													break
											if label_target:
												break
										if label_target == origen_label:
											l2["blocked"] = bool(bloquear)
											break
		if cambios:
			self._cargar()
			if callable(self.on_change):
				try:
					self.on_change()
				except Exception:
					pass
		else:
			messagebox.showinfo("Info", "No hubo cambios en los caminos seleccionados")
