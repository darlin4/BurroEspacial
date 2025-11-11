import tkinter as tk
from tkinter import ttk


class PanelCalculoRuta(tk.Frame):
	"""Panel que calcula la ruta que maximiza estrellas visitadas usando solo condiciones iniciales.

	El burro NO se alimenta durante el viaje; se degradan energía y pasto según distancia.
	Genera también un log detallado estilo consola para depuración que puede imprimirse en terminal.
	"""

	def __init__(self, master, grafo_provider, mapa_widget=None):
		super().__init__(master)
		self.grafo_provider = grafo_provider
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

		FACTOR_ENERGIA = 0.15  # % energía por unidad de distancia
		FACTOR_PASTO = 0.025   # kg pasto por unidad de distancia

		log(f"CALCULANDO RUTA DESDE: {estrella_origen}")
		log(f"   Energía inicial: {burroenergia:.1f}%")
		log(f"   Pasto inicial: {pasto:.1f} kg")
		log(f"   Salud inicial declarada: {salud_inicial}")
		log(f"   Vecinos disponibles desde {estrella_origen}: {list(grafo.get(estrella_origen, {}).keys())}")
		log("=" * 60)

		def dfs(actual, energia, pasto_rest, visitadas, consumos_ruta):
			nonlocal mejor_ruta, max_estrellas, mejor_detallados
			if energia <= 0 or pasto_rest <= 0:
				return
			if len(visitadas) > max_estrellas:
				max_estrellas = len(visitadas)
				mejor_ruta = visitadas.copy()
				mejor_detallados = consumos_ruta.copy()
				log(f"✨ ¡NUEVA MEJOR RUTA! {max_estrellas} estrellas")
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
					log("  ❌ Recursos insuficientes, no se puede visitar")
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
				dfs(destino, nueva_e, nuevo_p, visitadas + [destino], consumos_ruta + [next_step])

		dfs(estrella_origen, burroenergia, pasto, [estrella_origen], [])
		log("=" * 60)
		log("✅ BÚSQUEDA COMPLETADA")

		distancia_total = sum(c['distancia'] for c in mejor_detallados)
		energia_consumida_total = sum(c['consumo_energia'] for c in mejor_detallados)
		pasto_consumido_total = sum(c['consumo_pasto'] for c in mejor_detallados)
		energia_final = burroenergia - energia_consumida_total
		pasto_final = pasto - pasto_consumido_total

		estado_por_energia = self._obtener_estado_salud(max(0, energia_final))
		severidad = {"MUERTO": 5, "MORIBUNDO": 4, "MALO": 3, "BUENO": 2, "EXCELENTE": 1}
		ini = salud_inicial.upper()
		fin = estado_por_energia
		estado_final = fin if severidad.get(fin, 3) >= severidad.get(ini, 3) else ini

		log(f"   Mejor ruta encontrada: {mejor_ruta}")
		log(f"   Total de estrellas: {len(mejor_ruta)}")
		log(f"   Energía final: {max(0, energia_final):.1f}% | Pasto final: {max(0, pasto_final):.1f}kg")
		log(f"   Estado final: {estado_final}")

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
			"salud_inicial": ini
		}
		return resultado, "\n".join(log_lines)

	def _mostrar_resultado(self, r, log_text):
		t = self.txt_reporte
		t.delete("1.0", tk.END)
		self._imprimir("RUTA MÁXIMA", "titulo")
		self._imprimir(f"Salud inicial: {r['salud_inicial']}", "item")
		self._imprimir(f"Estado final: {r['estado_final']}", "resaltado" if r['estado_final'] != r['salud_inicial'] else "item")
		self._imprimir(f"Estrellas visitadas: {r['estrellas_visitadas']}", "item")
		self._imprimir(f"Distancia total: {r['distancia_total']:.1f}", "item")
		self._imprimir(f"Energía consumida: {r['energia_consumida_total']:.1f} / restante {r['energia_final']:.1f}", "item")
		self._imprimir(f"Pasto consumido: {r['pasto_consumido_total']:.2f} kg / restante {r['pasto_final']:.2f} kg", "item")
		self._imprimir("Ruta:", "titulo")
		self._imprimir(" -> ".join(r['ruta']) or "(vacía)", "ok")
		self._imprimir("Pasos detallados:", "titulo")
		for c in r['consumos_detallados']:
			linea = (f"{c['origen']} -> {c['destino']} | d={c['distancia']:.1f} | "
					 f"E-{c['consumo_energia']:.2f} (rest {c['energia_restante']:.2f}) | "
					 f"P-{c['consumo_pasto']:.2f} (rest {c['pasto_restante']:.2f})")
			self._imprimir(linea, "item")
		self._imprimir("="*40, "titulo")
		self._imprimir("LOG CONSOLA:", "titulo")
		for line in log_text.splitlines():
			tag = "item"
			if line.startswith("✨") or line.startswith("✅"):
				tag = "ok"
			elif line.startswith("❌"):
				tag = "critico"
			self._imprimir(line, tag)

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
