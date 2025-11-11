import tkinter as tk
from tkinter import ttk, messagebox


class PanelCalculoRuta(tk.Frame):
	"""Panel que calcula la ruta que maximiza estrellas visitadas usando solo condiciones iniciales.

	El burro NO se alimenta durante el viaje; se degradan energía y pasto según distancia.
	Genera también un log detallado estilo consola para depuración que puede imprimirse en terminal.
	"""

	def __init__(self, master, grafo_provider, data_provider=None, mapa_widget=None):
		super().__init__(master)
		self.grafo_provider = grafo_provider
		self.data_provider = data_provider
		self.mapa_widget = mapa_widget
		self._build_ui()

	def _build_ui(self):
		frm = ttk.Frame(self)
		frm.pack(fill="x", padx=8, pady=6)
		ttk.Label(frm, text="Estrella origen:").grid(row=0, column=0, sticky="w")
		self.combo_origen = ttk.Combobox(frm, width=20, state="readonly")
		self.combo_origen.grid(row=0, column=1, padx=4, pady=2)
		ttk.Button(frm, text="Refrescar", command=self._refrescar_origenes).grid(row=0, column=4, padx=4)
		ttk.Label(frm, text="Salud inicial:").grid(row=0, column=2, sticky="w")
		self.combo_salud = ttk.Combobox(frm, width=12, state="readonly",
			values=["EXCELENTE","BUENO","MALO","MORIBUNDO","MUERTO"])
		self.combo_salud.set("BUENO")
		self.combo_salud.grid(row=0, column=3, padx=4, pady=2)
		self.combo_salud.bind("<<ComboboxSelected>>", self._on_cambio_salud)
		ttk.Label(frm, text="Edad:").grid(row=1, column=0, sticky="w")
		self.entry_edad = ttk.Entry(frm, width=10)
		self.entry_edad.insert(0, "5")
		self.entry_edad.grid(row=1, column=1, padx=4, pady=2)
		ttk.Label(frm, text="Energía (%):").grid(row=1, column=2, sticky="w")
		self.entry_energia = ttk.Entry(frm, width=12)
		self.entry_energia.insert(0, "100")
		self.entry_energia.grid(row=1, column=3, padx=4, pady=2)
		ttk.Label(frm, text="Pasto (kg):").grid(row=2, column=0, sticky="w")
		self.entry_pasto = ttk.Entry(frm, width=10)
		self.entry_pasto.insert(0, "10")
		self.entry_pasto.grid(row=2, column=1, padx=4, pady=2)
		ttk.Button(frm, text="Calcular ruta", command=self._on_calcular).grid(row=2, column=3, padx=4, pady=4, sticky="e")

		# Llenar orígenes de inicio
		self._refrescar_origenes()

		self.txt_reporte = tk.Text(self, height=30, wrap="word", bg="#101010", fg="#eaeaea")
		self.txt_reporte.pack(fill="both", expand=True, padx=8, pady=6)
		self._config_tags()

		# Botón de reporte detallado
		frm_btns = ttk.Frame(self)
		frm_btns.pack(fill="x", padx=8, pady=(0,8))
		self.btn_reporte = ttk.Button(frm_btns, text="Reporte detallado", command=self._abrir_reporte_detallado)
		self.btn_reporte.pack(side="right")
		self._ultimo_resultado = None

	def _config_tags(self):
		t = self.txt_reporte
		t.tag_configure("titulo", font=("Segoe UI", 13, "bold"), foreground="#7AD1FF")
		t.tag_configure("item", font=("Consolas", 10), foreground="#C7F8FF")
		t.tag_configure("resaltado", font=("Consolas", 10, "bold"), foreground="#FFD86B")
		t.tag_configure("critico", font=("Consolas", 10, "bold"), foreground="#FF6B6B")
		t.tag_configure("ok", font=("Consolas", 10), foreground="#6BFF95")

	def _on_calcular(self):
		origen = (self.combo_origen.get() or "").strip()
		salud_ini = (self.combo_salud.get() or "BUENO").upper()
		try:
			edad = int(self.entry_edad.get())
		except ValueError:
			edad = 0
		try:
			energia = float(self.entry_energia.get())
		except ValueError:
			energia = 0
		try:
			pasto = float(self.entry_pasto.get())
		except ValueError:
			pasto = 0

		# Ajustar energía según salud (rangos cada 25%)
		RANGOS = {
			"EXCELENTE": (75, 100),
			"BUENO": (50, 75),
			"MALO": (25, 50),
			"MORIBUNDO": (0.000001, 25),  # evitar cero exacto para permitir un intento
			"MUERTO": (0, 0)
		}
		min_e, max_e = RANGOS.get(salud_ini, (50,75))
		energia_original = energia
		if energia < min_e:
			energia = min_e
		elif energia > max_e:
			energia = max_e
		energia = round(energia, 2)
		# Actualizar entrada si se normalizó
		if energia != energia_original:
			self.entry_energia.delete(0, tk.END)
			self.entry_energia.insert(0, str(energia))

		if salud_ini == "MUERTO" or energia <= 0:
			self._imprimir("Burro muerto: no puede iniciar viaje", "critico")
			return
		grafo = self.grafo_provider() if callable(self.grafo_provider) else {}
		if not origen or origen not in grafo:
			self._imprimir("Origen inválido o inexistente en grafo", "critico")
			return
		resultado, log = self._calcular_ruta_maxima(grafo, origen, energia, pasto, edad, salud_ini)
		self._ultimo_resultado = resultado
		self._mostrar_resultado(resultado, log)
		try:
			print(log)
		except Exception:
			pass
		if self.mapa_widget and hasattr(self.mapa_widget, "highlight_route"):
			try:
				self.mapa_widget.highlight_route(resultado["ruta"])
			except Exception:
				pass
		# Reproducir audio de muerte si ocurrió
		if resultado.get("murio"):
			self._reproducir_audio_muerte()

	def _refrescar_origenes(self):
		grafo = self.grafo_provider() if callable(self.grafo_provider) else {}
		opciones = sorted(grafo.keys())
		self.combo_origen["values"] = opciones
		if opciones and (self.combo_origen.get() not in opciones):
			self.combo_origen.set(opciones[0])

	def _on_cambio_salud(self, event=None):
		# Al cambiar salud, ajustar automáticamente energía al rango superior del estado
		estado = (self.combo_salud.get() or "BUENO").upper()
		RANGOS = {
			"EXCELENTE": (75, 100),
			"BUENO": (50, 75),
			"MALO": (25, 50),
			"MORIBUNDO": (0.000001, 25),
			"MUERTO": (0, 0)
		}
		_min_e, max_e = RANGOS.get(estado, (50,75))
		self.entry_energia.delete(0, tk.END)
		self.entry_energia.insert(0, str(max_e))

	def _obtener_estado_salud(self, energia):
		if energia <= 0:
			return "MUERTO"
		elif energia <= 25:
			return "MORIBUNDO"
		elif energia <= 50:
			return "MALO"
		elif energia <= 75:
			return "BUENO"
		else:
			return "EXCELENTE"

	def _calcular_ruta_maxima(self, grafo, estrella_origen, burroenergia, pasto, edad, salud_inicial):
		mejor_ruta = []
		max_estrellas = 0
		mejor_detallados = []
		log_lines = []

		def log(line):
			log_lines.append(line)

		# Factores de consumo calibrados para permitir varios saltos y aún así poder morir
		FACTOR_ENERGIA = 0.35   # % energía por unidad de distancia (p.ej. 120 -> 42%)
		FACTOR_PASTO = 0.02     # kg pasto por unidad de distancia (p.ej. 120 -> 2.4kg)

		log(f"CALCULANDO RUTA DESDE: {estrella_origen}")
		log(f"   Energía inicial: {burroenergia:.1f}%")
		log(f"   Pasto inicial: {pasto:.1f} kg")
		log(f"   Salud inicial declarada: {salud_inicial}")
		log(f"   Vecinos disponibles desde {estrella_origen}: {list(grafo.get(estrella_origen, {}).keys())}")
		log("=" * 60)

		# Guardar información de una muerte potencial en el recorrido elegido
		mejor_muerte = None  # dict: {desde, hacia, causa, energia_antes, pasto_antes, distancia}
		saltos_mortales = []  # Lista de saltos que causarían muerte

		def dfs(actual, energia, pasto_rest, visitadas, consumos_ruta, muerte=None):
			nonlocal mejor_ruta, max_estrellas, mejor_detallados, mejor_muerte, saltos_mortales
			if energia <= 0 or pasto_rest <= 0:
				# Llegó sin recursos al comienzo del nodo (muerte por agotamiento)
				if len(visitadas) >= max_estrellas:
					mejor_ruta = visitadas.copy()
					mejor_detallados = consumos_ruta.copy()
					max_estrellas = len(visitadas)
					mejor_muerte = muerte or {
						"desde": actual,
						"hacia": None,
						"causa": "energia" if energia <= 0 else "pasto",
						"energia_antes": max(0.0, energia),
						"pasto_antes": max(0.0, pasto_rest),
						"distancia": 0.0
					}
				return
			# Actualizar mejor ruta (preferir la que conduce a muerte en caso de empate de estrellas)
			if len(visitadas) > max_estrellas or (len(visitadas) == max_estrellas and (muerte is not None and mejor_muerte is None)):
				max_estrellas = len(visitadas)
				mejor_ruta = visitadas.copy()
				mejor_detallados = consumos_ruta.copy()
				mejor_muerte = muerte
				log(f"✨ ¡NUEVA MEJOR RUTA! {max_estrellas} estrellas" + (" (con muerte)" if muerte else ""))
			log(f"📍 En {actual} | E={energia:.1f}% P={pasto_rest:.1f}kg | Visitadas={len(visitadas)}")
			for destino, distancia in grafo.get(actual, {}).items():
				if destino in visitadas:
					continue
				consumo_e = distancia * FACTOR_ENERGIA
				consumo_p = distancia * FACTOR_PASTO
				nueva_e = energia - consumo_e
				nuevo_p = pasto_rest - consumo_p
				log(f"🔍 Probando {actual} -> {destino} (dist={distancia:.1f})")
				log(f"   Consumo: E={consumo_e:.1f}% P={consumo_p:.1f}kg")
				log(f"   Resultado: E={nueva_e:.1f}% P={nuevo_p:.1f}kg")
				if nueva_e <= 0 or nuevo_p <= 0:
					# Registrar muerte al intentar este salto; no se visita el destino
					causa = "energia" if nueva_e <= 0 and (nuevo_p > 0 or nueva_e <= nuevo_p) else "pasto"
					info_muerte = {
						"desde": actual,
						"hacia": destino,
						"causa": causa,
						"energia_antes": energia,
						"pasto_antes": pasto_rest,
						"distancia": distancia,
						"ruta_previa": visitadas.copy(),
						"consumos_previos": consumos_ruta.copy()
					}
					log("  ☠️  Muerte si intenta este salto")
					# Guardar como salto mortal candidato (NO marcar mejor_muerte automáticamente)
					saltos_mortales.append(info_muerte)
					continue
				log("✅ Suficientes recursos, explorando...")
				next_step = {
					"origen": actual,
					"destino": destino,
					"distancia": distancia,
					"consumo_energia": consumo_e,
					"consumo_pasto": consumo_p,
					"energia_restante": nueva_e,
					"pasto_restante": nuevo_p
				}
				dfs(destino, nueva_e, nuevo_p, visitadas + [destino], consumos_ruta + [next_step], muerte)

		dfs(estrella_origen, burroenergia, pasto, [estrella_origen], [])
		log("=" * 60)
		log("✅ BÚSQUEDA COMPLETADA")

		# Si hay saltos mortales posibles, preguntar si quiere arriesgarse
		if saltos_mortales:
			# Seleccionar el salto mortal más prometedor (el de la ruta más larga)
			salto_candidato = max(saltos_mortales, key=lambda x: len(x.get('ruta_previa', [])))
			
			# Crear diálogo personalizado más bonito
			respuesta = self._dialogo_salto_mortal(salto_candidato)
			
			if respuesta:
				# Usuario acepta el riesgo: marcar muerte
				mejor_muerte = salto_candidato
				mejor_ruta = salto_candidato['ruta_previa']
				mejor_detallados = salto_candidato['consumos_previos']
				log("⚠️ USUARIO ACEPTÓ SALTO MORTAL - El burro morirá")
			else:
				# Usuario rechaza: mantener ruta segura y generar reporte sin muerte
				log("⛔ Usuario rechazó salto mortal - Ruta segura confirmada")
				log(f"   El burro visitó {len(mejor_ruta)} estrellas sin arriesgarse")

		distancia_total = sum(c['distancia'] for c in mejor_detallados)
		energia_consumida_total = sum(c['consumo_energia'] for c in mejor_detallados)
		pasto_consumido_total = sum(c['consumo_pasto'] for c in mejor_detallados)
		energia_final = burroenergia - energia_consumida_total
		pasto_final = pasto - pasto_consumido_total

		estado_por_energia = self._obtener_estado_salud(max(0, energia_final))
		severidad = {"MUERTO": 5, "MORIBUNDO": 4, "MALO": 3, "BUENO": 2, "EXCELENTE": 1}
		ini = salud_inicial.upper()
		fin = estado_por_energia
		# Si hubo muerte en el último intento, forzar MUERTO
		murio = mejor_muerte is not None
		estado_final = "MUERTO" if murio else (fin if severidad.get(fin, 3) >= severidad.get(ini, 3) else ini)

		log(f"   Mejor ruta encontrada: {mejor_ruta}")
		log(f"   Total de estrellas: {len(mejor_ruta)}")
		log(f"   Energía final: {max(0, energia_final):.1f}% | Pasto final: {max(0, pasto_final):.1f}kg")
		log(f"   Estado final: {estado_final}")
		if murio:
			log(f"   Murió al intentar ir de {mejor_muerte['desde']} a {mejor_muerte['hacia']} por falta de {mejor_muerte['causa']}")

		# Datos de galaxias visitadas usando el data_provider
		galaxias = []
		if self.data_provider:
			data = self.data_provider() or {}
			consts = data.get('constellations', [])
			label_to_gal = {}
			for c in consts:
				gname = c.get('name')
				for s in c.get('starts', []):
					label_to_gal[s.get('label')] = gname
			for lab in mejor_ruta:
				gal = label_to_gal.get(lab)
				if gal and gal not in galaxias:
					galaxias.append(gal)

		resultado = {
			"ruta": mejor_ruta,
			"estrellas_visitadas": len(mejor_ruta),
			"estado_final": estado_final,
			"energia_final": max(0, energia_final),
			"pasto_final": max(0, pasto_final),
			"distancia_total": distancia_total,
			"energia_consumida_total": energia_consumida_total,
			"pasto_consumido_total": pasto_consumido_total,
			"consumos_detallados": mejor_detallados,
			"salud_inicial": ini,
			"galaxias": galaxias,
			"murio": murio,
			"muerte_info": mejor_muerte
		}
		return resultado, "\n".join(log_lines)

	def _mostrar_resultado(self, r, log_text):
		t = self.txt_reporte
		t.delete("1.0", tk.END)
		self._imprimir("RUTA MÁXIMA", "titulo")
		self._imprimir(f"Salud inicial: {r['salud_inicial']}", "item")
		self._imprimir(f"Estado final: {r['estado_final']}", "resaltado" if r['estado_final'] != r['salud_inicial'] else "item")
		if r.get('murio') and r.get('muerte_info'):
			mi = r['muerte_info']
			self._imprimir(f"Murió al intentar ir de {mi['desde']} a {mi['hacia']} por falta de {mi['causa']}", "critico")
		self._imprimir(f"Estrellas visitadas: {r['estrellas_visitadas']}", "item")
		self._imprimir(f"Distancia total: {r['distancia_total']:.1f}", "item")
		self._imprimir(f"Energía consumida: {r['energia_consumida_total']:.1f} / restante {r['energia_final']:.1f}", "item")
		self._imprimir(f"Pasto consumido: {r['pasto_consumido_total']:.2f} kg / restante {r['pasto_final']:.2f} kg", "item")
		self._imprimir("Galaxias:", "titulo")
		self._imprimir(", ".join(r.get('galaxias', [])) or "(ninguna)", "item")
		self._imprimir("Ruta (orden):", "titulo")
		self._imprimir(" -> ".join(r['ruta']) or "(vacía)", "ok")
		self._imprimir("Consumos por salto (alimento y energía):", "titulo")
		self._imprimir("Pasos detallados:", "titulo")
		invest_tiempo_total = 0.0
		for idx, c in enumerate(r['consumos_detallados'], start=1):
			# tiempo invertido en investigación: suponer 0.3 * distancia / (energia_restante+1) como ejemplo (placeholder SOLID: estrategia posible)
			tiempo = 0.3 * c['distancia'] / (c['energia_restante'] + 1)
			invest_tiempo_total += tiempo
			linea = (f"{idx:02d}. {c['origen']} -> {c['destino']} | d={c['distancia']:.1f} | "
					 f"E usó {c['consumo_energia']:.2f} (rest {c['energia_restante']:.2f}) | "
					 f"P usó {c['consumo_pasto']:.2f} (rest {c['pasto_restante']:.2f}) | "
					 f"tInvestigación={tiempo:.2f}")
			self._imprimir(linea, "item")
		self._imprimir(f"Tiempo total investigación estimado: {invest_tiempo_total:.2f}", "resaltado")
		self._imprimir("="*40, "titulo")
		self._imprimir("LOG CONSOLA:", "titulo")
		for line in log_text.splitlines():
			tag = "item"
			if line.startswith("✨") or line.startswith("✅"):
				tag = "ok"
			elif line.startswith("❌"):
				tag = "critico"
			self._imprimir(line, tag)

	def _abrir_reporte_detallado(self):
		if not self._ultimo_resultado:
			return
		r = self._ultimo_resultado
		win = tk.Toplevel(self)
		win.title("Reporte de Viaje Detallado")
		win.geometry("800x520")
		# Fade-in sencillo
		try:
			win.attributes("-alpha", 0.0)
			def fade(i=0):
				alpha = min(1.0, i/10)
				win.attributes("-alpha", alpha)
				if alpha < 1.0:
					win.after(35, lambda: fade(i+1))
			fade()
		except Exception:
			pass
		cols = ("#", "Estrella", "Galaxia", "Distancia", "Energía", "Pasto", "Investigación")
		tree = ttk.Treeview(win, columns=cols, show="headings")
		for c in cols:
			tree.heading(c, text=c)
			tree.column(c, width=110, anchor="center")
		tree.column("Estrella", width=160, anchor="w")
		tree.column("Galaxia", width=160, anchor="w")
		tree.pack(fill="both", expand=True, padx=8, pady=8)
		# construir mapa label->galaxia
		gal_by_label = {}
		if self.data_provider:
			data = self.data_provider() or {}
			for c in data.get('constellations', []):
				for s in c.get('starts', []):
					gal_by_label[s.get('label')] = c.get('name')
		# fila de origen
		if r['ruta']:
			ori = r['ruta'][0]
			tree.insert("", "end", values=("00", ori, gal_by_label.get(ori, ""), "-", "-", "-", "0.00"))
		# filas de saltos
		invest_total = 0.0
		for i, c in enumerate(r['consumos_detallados'], start=1):
			ori = c['origen']
			dst = c['destino']
			dist = f"{c['distancia']:.1f}"
			ener = f"{c['consumo_energia']:.2f}"
			past = f"{c['consumo_pasto']:.2f}"
			tiempo = 0.3 * c['distancia'] / (c['energia_restante'] + 1)
			invest_total += tiempo
			gal = gal_by_label.get(dst, "")
			tree.insert("", "end", values=(f"{i:02d}", dst, gal, dist, ener, past, f"{tiempo:.2f}"))
		# totales
		texto_footer = (
			f"Estrellas: {r['estrellas_visitadas']} | Galaxias: {len(r.get('galaxias', []))} | "
			f"Distancia total: {r['distancia_total']:.1f} | Energía usada: {r['energia_consumida_total']:.1f} | "
			f"Pasto usado: {r['pasto_consumido_total']:.2f} | Investigación: {invest_total:.2f}"
		)
		if r.get('murio') and r.get('muerte_info'):
			mi = r['muerte_info']
			texto_footer += f" | ☠️ Muerte: {mi['desde']} → {mi['hacia']} por {mi['causa']}"
		footer = ttk.Label(win, text=texto_footer)
		footer.pack(fill="x", padx=8, pady=(0,8))

	def _reproducir_audio_muerte(self):
		"""Reproduce un audio cuando el burro muere. Coloca tu archivo en assets/sounds/burro_muerte.wav

		En Windows se usa winsound. En otros sistemas intenta con simpleaudio si estuviera instalado.
		"""
		import os, sys
		ruta = os.path.join(os.path.dirname(sys.modules.get(__name__).__file__), "..", "..", "assets", "burro.wav")
		try:
			if os.path.exists(ruta):
				try:
					import winsound
					winsound.PlaySound(ruta, winsound.SND_FILENAME | winsound.SND_ASYNC)
					return
				except Exception:
					pass
		except Exception:
			pass
		# Si no se pudo reproducir, registrar en el log del panel
		self._imprimir("[Audio muerte no disponible]", "critico")

	def _dialogo_salto_mortal(self, salto):
		"""Muestra un diálogo personalizado bonito para preguntar si arriesgarse al salto mortal (layout con grid)"""
		dialogo = tk.Toplevel(self)
		dialogo.title("⚠️ Decisión Crítica")
		dialogo.configure(bg="#1a1a2e")
		dialogo.minsize(520, 420)
		dialogo.geometry("520x420")
		dialogo.resizable(False, False)

		# Modal y topmost breve
		dialogo.transient(self)
		dialogo.grab_set()
		dialogo.lift()
		dialogo.attributes('-topmost', True)
		dialogo.after(250, lambda: dialogo.attributes('-topmost', False))

		# Centrar
		dialogo.update_idletasks()
		sx = (dialogo.winfo_screenwidth() // 2) - (520 // 2)
		sy = (dialogo.winfo_screenheight() // 2) - (420 // 2)
		dialogo.geometry(f"520x420+{sx}+{sy}")

		# Grid config
		dialogo.grid_columnconfigure(0, weight=1)
		for r in (0,1,2,3,4,5):
			dialogo.grid_rowconfigure(r, weight=0)
		dialogo.grid_rowconfigure(3, weight=1)  # espaciador para empujar botones abajo

		# Título y subtítulo
		lbl_titulo = tk.Label(dialogo, text="⚠️ SALTO MORTAL DETECTADO ⚠️",
							 font=("Segoe UI", 16, "bold"), fg="#ff6b6b", bg="#1a1a2e")
		lbl_titulo.grid(row=0, column=0, padx=20, pady=(18, 6), sticky="nwe")

		lbl_sub = tk.Label(dialogo, text="El burro puede intentar un último salto arriesgado...",
						  font=("Segoe UI", 10), fg="#c7f8ff", bg="#1a1a2e")
		lbl_sub.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="we")

		# Panel info
		frm_info = tk.Frame(dialogo, bg="#16213e", relief="ridge", bd=2)
		frm_info.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="we")

		info_items = [
			("Desde:", salto['desde'], "#7ad1ff"),
			("Hacia:", salto['hacia'], "#7ad1ff"),
			("Distancia:", f"{salto['distancia']:.1f}", "#ffd86b"),
			("Causa de muerte:", f"Falta de {salto['causa']}", "#ff6b6b"),
			("Energía antes:", f"{salto['energia_antes']:.1f}%", "#6bff95"),
			("Pasto antes:", f"{salto['pasto_antes']:.1f} kg", "#6bff95")
		]
		for idx, (label, valor, color) in enumerate(info_items):
			row = tk.Frame(frm_info, bg="#16213e")
			row.pack(fill="x", padx=12, pady=4)
			tk_lbl = tk.Label(row, text=label, font=("Consolas", 10, "bold"), fg="#eaeaea", bg="#16213e", width=18, anchor="w")
			tk_val = tk.Label(row, text=valor, font=("Consolas", 10), fg=color, bg="#16213e", anchor="w")
			tk_lbl.pack(side="left")
			tk_val.pack(side="left", fill="x", expand=True)

		# Espaciador para empujar botones
		sp = tk.Frame(dialogo, bg="#1a1a2e")
		sp.grid(row=3, column=0, sticky="nswe")

		# Pregunta
		lbl_preg = tk.Label(dialogo, text="¿Desea que el burro lo intente de todas formas?",
						  font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#1a1a2e")
		lbl_preg.grid(row=4, column=0, padx=20, pady=(6, 8), sticky="we")

		# Respuesta mutable
		respuesta = [False]
		def aceptar():
			respuesta[0] = True
			dialogo.destroy()
		def rechazar():
			respuesta[0] = False
			dialogo.destroy()

		# Botonera
		frm_btns = tk.Frame(dialogo, bg="#1a1a2e")
		frm_btns.grid(row=5, column=0, padx=20, pady=(2, 16), sticky="swe")
		frm_btns.grid_columnconfigure(0, weight=1)
		frm_btns.grid_columnconfigure(1, weight=1)

		btn_si = tk.Button(frm_btns, text="SÍ, ARRIESGARSE", font=("Segoe UI", 12, "bold"),
						  bg="#ff6b6b", fg="#ffffff", activebackground="#ff5252",
						  activeforeground="#ffffff", relief="solid", bd=2,
						  height=2, command=aceptar)
		btn_no = tk.Button(frm_btns, text="NO, RUTA SEGURA", font=("Segoe UI", 12, "bold"),
						  bg="#6bff95", fg="#1a1a2e", activebackground="#5eeb87",
						  activeforeground="#1a1a2e", relief="solid", bd=2,
						  height=2, command=rechazar)
		btn_si.grid(row=0, column=0, padx=(0, 8), sticky="we")
		btn_no.grid(row=0, column=1, padx=(8, 0), sticky="we")

		# Fade-in
		dialogo.attributes("-alpha", 0.0)
		def fade(alpha=0.0):
			if alpha < 1.0:
				alpha += 0.1
				dialogo.attributes("-alpha", alpha)
				dialogo.after(18, lambda: fade(alpha))
		dialogo.after(10, fade)

		# Esperar
		dialogo.wait_window()
		return respuesta[0]

	def _imprimir(self, texto, tag=None):
		self.txt_reporte.insert(tk.END, texto + "\n", tag)
		self.txt_reporte.see(tk.END)


if __name__ == "__main__":
	# Prueba rápida manual
	ejemplo = {
		"Alpha": {"Beta": 50, "Gamma": 30},
		"Beta": {"Delta": 80},
		"Gamma": {"Delta": 70},
		"Delta": {}
	}
	root = tk.Tk()
	root.title("Test PanelCalculoRuta")
	p = PanelCalculoRuta(root, grafo_provider=lambda: ejemplo)
	p.pack(fill="both", expand=True)
	p.entry_origen.insert(0, "Alpha")
	root.mainloop()
