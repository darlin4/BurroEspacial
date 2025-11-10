import json
import os
from typing import Dict

# optional optimizer import
try:
    from utils.algorithms.pathfinding import propose_route
except Exception:
    propose_route = None

# optional helpers (may be None if not available)
try:
    from utils import SoundHelper
except Exception:
    SoundHelper = None

# === UI (Tkinter) ===
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext


def estado_salud_por_energia(energia):
    if energia <= 0:
        return "muerto"
    elif energia <= 25:
        return "moribundo"
    elif energia <= 50:
        return "mala"
    elif energia <= 75:
        return "buena"
    else:
        return "excelente"


def cargar_grafo_desde_json(ruta_json):
    """Genera un grafo en formato {nombre: {vecino: distancia}} desde Constellations.json."""
    if not os.path.exists(ruta_json):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_json}")

    with open(ruta_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    grafo = {}
    for const in data.get("constellations", []):
        for star in const.get("starts", []):
            nombre = star["label"]
            grafo[nombre] = {}
            for enlace in star.get("linkedTo", []):
                if enlace.get("blocked", False):
                    continue
                destino_id = enlace["starId"]
                distancia = enlace["distance"]

                destino_nombre = None
                for c2 in data["constellations"]:
                    for s2 in c2["starts"]:
                        if s2["id"] == destino_id:
                            destino_nombre = s2["label"]
                            break
                    if destino_nombre:
                        break

                if destino_nombre:
                    grafo[nombre][destino_nombre] = distancia
    return grafo


def ruta_maxima(estrella_origen, salud_inicial, edad, burroenergia, pasto_bodega, grafo):
    """Calcula la ruta más larga posible antes de que el burro muera."""
    mejor_ruta = []
    max_estrellas = 0
    
    # Factores de consumo según salud (más realistas)
    factores_salud = {
        "excelente": 0.5,  # Consume menos energía
        "buena": 0.7,
        "mala": 1.0,
        "moribundo": 1.5,
        "muerto": 999.0
    }
    
    factor_consumo = factores_salud.get(salud_inicial.lower(), 1.0)

    def dfs(actual, energia, pasto, tiempo_vida, visitadas, pasos_detalle):
        nonlocal mejor_ruta, max_estrellas
        
        # Condiciones de muerte
        if energia <= 0 or pasto <= 0 or tiempo_vida <= 0:
            return
            
        if len(visitadas) > max_estrellas:
            mejor_ruta = visitadas.copy()
            max_estrellas = len(visitadas)

        for destino, distancia in grafo.get(actual, {}).items():
            if destino in visitadas:
                continue
            
            # Cálculos de consumo más realistas
            # Consumo de energía: distancia * factor de salud (0.5-1.5% por unidad)
            consumo_energia = distancia * factor_consumo * 0.5
            
            # Consumo de pasto: aproximadamente 0.05 kg por unidad de distancia
            consumo_pasto = distancia * 0.05
            
            # Tiempo de vida: se reduce por la distancia viajada
            consumo_tiempo = distancia
            
            # Calcular nuevos valores
            nueva_energia = energia - consumo_energia
            nuevo_pasto = pasto - consumo_pasto
            nuevo_tiempo = tiempo_vida - consumo_tiempo
            
            # Si necesita pasto y tiene disponible, comer automáticamente
            if nueva_energia < 50 and nuevo_pasto > 0:
                # Comer hasta recuperar energía (máximo disponible)
                pasto_a_comer = min(nuevo_pasto, (50 - nueva_energia) / 5)  # 1kg = 5% energía
                nueva_energia += pasto_a_comer * 5
                nuevo_pasto -= pasto_a_comer
            
            # Verificar si puede continuar
            if nueva_energia > 0 and nuevo_pasto > 0 and nuevo_tiempo > 0:
                nuevo_detalle = pasos_detalle + [{
                    'destino': destino,
                    'distancia': distancia,
                    'energia_consumida': consumo_energia,
                    'pasto_consumido': consumo_pasto,
                    'energia_restante': nueva_energia,
                    'pasto_restante': nuevo_pasto
                }]
                dfs(destino, nueva_energia, nuevo_pasto, nuevo_tiempo, 
                    visitadas + [destino], nuevo_detalle)

    # Tiempo de vida inicial basado en la edad (más joven = más tiempo)
    tiempo_vida_inicial = max(100, 500 - (edad * 10))
    
    dfs(estrella_origen, burroenergia, pasto_bodega, tiempo_vida_inicial, [estrella_origen], [])

    estado_final = estado_salud_por_energia(burroenergia - (max_estrellas * 10))
    return {
        "ruta": mejor_ruta,
        "estrellas_visitadas": max_estrellas,
        "estado_final": estado_final,
        "energia_inicial": burroenergia,
        "pasto_inicial": pasto_bodega,
        "factor_salud": salud_inicial,
        "edad": edad
    }


# =========================
# Panel Tkinter para la UI
# =========================

class PanelRutas(tk.Frame):
    """
    Panel visual para calcular la ruta máxima de estrellas visitadas
    usando únicamente las condiciones iniciales. Envuelve las funciones
    cargar_grafo_desde_json y ruta_maxima.
    """

    def __init__(self, parent, mapa=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#0b0c10")

        self.grafo = {}
        # optional map widget reference to draw routes
        self.mapa = mapa

        self._build_ui()

    # --- API para integrarse con MainWindow ---
    def set_grafo_from_json(self, ruta_json: str):
        """Carga el grafo desde un archivo JSON y actualiza combos."""
        try:
            self.grafo = cargar_grafo_desde_json(ruta_json)
            self._update_origenes()
            
            # Actualizar label de estado
            num_estrellas = len(self.grafo)
            num_conexiones = sum(len(vecinos) for vecinos in self.grafo.values())
            self.label_status.config(
                text=f"✅ Grafo cargado: {num_estrellas} estrellas, {num_conexiones} conexiones",
                fg="#44ff44"
            )
            print(f"✅ Grafo cargado: {num_estrellas} estrellas, {num_conexiones} conexiones")
            
        except Exception as e:
            self.label_status.config(
                text=f"❌ Error al cargar grafo",
                fg="#ff4444"
            )
            messagebox.showerror("Error", f"No se pudo cargar el grafo:\n{e}")

        # Validate hypergiant counts per galaxy (max 2 per galaxy requirement)
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            counts = {}
            for c in data.get('constellations', []):
                for s in c.get('starts', []):
                    if s.get('hypergiant'):
                        g = s.get('galaxy', None)
                        counts[g] = counts.get(g, 0) + 1
            violations = [g for g, cnt in counts.items() if cnt > 2]
            if violations:
                messagebox.showwarning('Advertencia', f"Se detectaron más de 2 hipergigantes en las galaxias: {violations}. Esto excede la restricción (max 2 por galaxia). El optimizador seguirá funcionando, pero revise el JSON.")
        except Exception:
            pass

    # --- Construcción de UI ---
    def _build_ui(self):
        # Título
        lbl = tk.Label(self, text="🚀 Calculador de Ruta Máxima", bg="#0b0c10", fg="#00eaff", font=("Orbitron", 14, "bold"))
        lbl.pack(pady=8)

        frm = tk.LabelFrame(self, text="Condiciones Iniciales", bg="#0b0c10", fg="white")
        frm.pack(fill="x", padx=8, pady=6)

        # Origen
        tk.Label(frm, text="Estrella Origen:", bg="#0b0c10", fg="white").grid(row=0, column=0, sticky="w", padx=4, pady=3)
        self.combo_origen = ttk.Combobox(frm, state="readonly", width=26)
        self.combo_origen.grid(row=0, column=1, padx=4, pady=3, sticky="ew")

        # Salud
        tk.Label(frm, text="Salud:", bg="#0b0c10", fg="white").grid(row=1, column=0, sticky="w", padx=4, pady=3)
        self.combo_salud = ttk.Combobox(frm, values=["excelente", "buena", "mala", "moribundo"], state="readonly", width=26)
        self.combo_salud.grid(row=1, column=1, padx=4, pady=3, sticky="ew")
        self.combo_salud.current(0)

        # Edad
        tk.Label(frm, text="Edad (años):", bg="#0b0c10", fg="white").grid(row=2, column=0, sticky="w", padx=4, pady=3)
        self.entry_edad = tk.Entry(frm, width=28)
        self.entry_edad.insert(0, "5.0")
        self.entry_edad.grid(row=2, column=1, padx=4, pady=3, sticky="ew")

        # Energía
        tk.Label(frm, text="Burroenergía (%):", bg="#0b0c10", fg="white").grid(row=3, column=0, sticky="w", padx=4, pady=3)
        self.entry_energia = tk.Entry(frm, width=28)
        self.entry_energia.insert(0, "100")
        self.entry_energia.grid(row=3, column=1, padx=4, pady=3, sticky="ew")

        # Pasto
        tk.Label(frm, text="Pasto (kg):", bg="#0b0c10", fg="white").grid(row=4, column=0, sticky="w", padx=4, pady=3)
        self.entry_pasto = tk.Entry(frm, width=28)
        self.entry_pasto.insert(0, "10")
        self.entry_pasto.grid(row=4, column=1, padx=4, pady=3, sticky="ew")

        frm.columnconfigure(1, weight=1)

        # Acciones
        actions = tk.Frame(self, bg="#0b0c10")
        actions.pack(fill="x", padx=8, pady=6)

        self.btn_cargar_json = ttk.Button(actions, text="Cargar JSON…", command=self._on_cargar_json)
        self.btn_cargar_json.pack(side="left")

        self.btn_calc = ttk.Button(actions, text="Calcular Ruta", command=self._on_calcular)
        self.btn_calc.pack(side="left", padx=6)

        # Optimized route (minimizar gasto)
        self.btn_calc_opt = ttk.Button(actions, text="Calcular Ruta (optimizada)", command=self._on_calcular_optimizada)
        self.btn_calc_opt.pack(side="left", padx=6)
        
        # Label de estado
        self.label_status = tk.Label(
            self, 
            text="Carga un JSON o el sistema usará el cargado en el mapa",
            bg="#0b0c10",
            fg="#888",
            font=("Arial", 9)
        )
        self.label_status.pack(pady=3)

        # Resultados
        frm_res = tk.LabelFrame(self, text="Resultados", bg="#0b0c10", fg="white")
        frm_res.pack(fill="both", expand=True, padx=8, pady=6)

        self.txt = scrolledtext.ScrolledText(frm_res, height=16, bg="#1a1a1a", fg="white", font=("Consolas", 9))
        self.txt.pack(fill="both", expand=True, padx=6, pady=6)

    def _update_origenes(self):
        nombres = sorted(list(self.grafo.keys()))
        self.combo_origen["values"] = nombres
        if nombres:
            self.combo_origen.current(0)

    # --- Acciones ---
    def _on_cargar_json(self):
        ruta = filedialog.askopenfilename(title="Seleccionar Constellations.json", filetypes=[("JSON", "*.json")])
        if not ruta:
            return
        self.set_grafo_from_json(ruta)

    def _on_calcular(self):
        if not self.grafo:
            messagebox.showwarning("Atención", "Carga primero un JSON de constelaciones")
            return

        origen = self.combo_origen.get()
        if not origen:
            messagebox.showwarning("Atención", "Selecciona la estrella de origen")
            return

        try:
            salud = self.combo_salud.get()
            edad = float(self.entry_edad.get())
            energia = float(self.entry_energia.get())
            pasto = float(self.entry_pasto.get())
        except ValueError:
            messagebox.showerror("Error", "Verifica que edad, energía y pasto sean números válidos")
            return

        # Validaciones
        if not (0 <= energia <= 100):
            messagebox.showerror("Error", "La burroenergía debe estar entre 0 y 100%")
            return
        
        if pasto <= 0:
            messagebox.showerror("Error", "El pasto debe ser mayor a 0 kg")
            return
        
        if edad < 0:
            messagebox.showerror("Error", "La edad no puede ser negativa")
            return

        # Calcular ruta
        res = ruta_maxima(origen, salud, edad, energia, pasto, self.grafo)

        # Mostrar resultados
        self.txt.delete("1.0", tk.END)
        self.txt.insert(tk.END, "═" * 80 + "\n")
        self.txt.insert(tk.END, "  RUTA CALCULADA - MÁXIMAS ESTRELLAS CON CONDICIONES INICIALES\n")
        self.txt.insert(tk.END, "═" * 80 + "\n\n")
        
        # Condiciones iniciales
        self.txt.insert(tk.END, "📋 CONDICIONES INICIALES:\n")
        self.txt.insert(tk.END, f"  • Estrella Origen: {origen}\n")
        self.txt.insert(tk.END, f"  • Estado de Salud: {salud.upper()}\n")
        self.txt.insert(tk.END, f"  • Edad: {edad} años\n")
        self.txt.insert(tk.END, f"  • Burroenergía: {energia}%\n")
        self.txt.insert(tk.END, f"  • Pasto en Bodega: {pasto} kg\n\n")
        
        # Resultados
        self.txt.insert(tk.END, "🎯 RESULTADOS:\n")
        self.txt.insert(tk.END, f"  • Estrellas Visitadas: {res['estrellas_visitadas']}\n")
        
        if res['ruta'] and len(res['ruta']) > 0:
            self.txt.insert(tk.END, f"  • Estado Final (estimado): {res['estado_final'].upper()}\n\n")
            
            # Mostrar ruta
            self.txt.insert(tk.END, "🛣️  RUTA ÓPTIMA:\n")
            self.txt.insert(tk.END, "  " + " → ".join(res['ruta']) + "\n\n")
            
            # Calcular distancia total
            distancia_total = 0
            for i in range(len(res['ruta']) - 1):
                actual = res['ruta'][i]
                siguiente = res['ruta'][i + 1]
                if siguiente in self.grafo.get(actual, {}):
                    distancia_total += self.grafo[actual][siguiente]
            
            self.txt.insert(tk.END, f"  📏 Distancia Total: {distancia_total:.1f} años luz\n")
            
            # Información adicional
            self.txt.insert(tk.END, "\n💡 INFORMACIÓN:\n")
            self.txt.insert(tk.END, f"  • El burro visita {res['estrellas_visitadas']} estrellas en total\n")
            self.txt.insert(tk.END, f"  • Cálculo basado únicamente en valores iniciales\n")
            self.txt.insert(tk.END, f"  • Los caminos bloqueados no son considerados\n")
            
        else:
            self.txt.insert(tk.END, "\n⚠️  NO SE ENCONTRÓ RUTA POSIBLE\n")
            self.txt.insert(tk.END, "  Posibles razones:\n")
            self.txt.insert(tk.END, "  • Energía o pasto insuficientes\n")
            self.txt.insert(tk.END, "  • Todos los caminos están bloqueados\n")
            self.txt.insert(tk.END, "  • Estrella origen aislada\n")
        
        self.txt.insert(tk.END, "\n" + "═" * 80 + "\n")

    def _build_label_for_opt(self, res: Dict):
        lines = []
        lines.append("═" * 80)
        lines.append("  RUTA CALCULADA - MÁXIMAS ESTRELLAS (OPTIMIZADA)")
        lines.append("═" * 80)
        lines.append("")
        lines.append("📋 CONDICIONES INICIALES:")
        lines.append(f"  • Estrella Origen: {self.combo_origen.get()}")
        lines.append(f"  • Burroenergía inicial: {res.get('energia_inicial', '')}")
        lines.append(f"  • Pasto inicial: {res.get('pasto_inicial', '')}")
        lines.append("")
        lines.append("🎯 RESULTADOS:")
        lines.append(f"  • Estrellas Visitadas: {res.get('estrellas_visitadas', 0)}")
        if res.get('ruta'):
            lines.append(f"  • Ruta: {' -> '.join(res.get('ruta'))}")
            lines.append(f"  • Energia final (estimada): {res.get('energia_final', '')}")
            lines.append(f"  • Pasto final (estimado): {res.get('pasto_final', '')}")
            lines.append(f"  • Tiempo de vida final: {res.get('tiempo_vida_final', '')}")
            # pasos detallados si están disponibles
            pasos = res.get('pasos', [])
            if pasos:
                lines.append("")
                lines.append("🔎 DETALLE DE PASOS:")
                for i, p in enumerate(pasos, start=1):
                    desde = p.get('desde')
                    hacia = p.get('hacia')
                    dist = p.get('distancia')
                    vida = p.get('tiempo_vida_restante')
                    eaten = p.get('eaten_kg', 0)
                    jump = p.get('jump_to')
                    if jump:
                        lines.append(f"  {i}. {desde} -> {hacia} (dist {dist}) -> JUMP to {jump} | Vida restante: {vida:.1f} | Pasto comido: {eaten}")
                    else:
                        lines.append(f"  {i}. {desde} -> {hacia} (dist {dist}) | Vida restante: {vida:.1f} | Pasto comido: {eaten}")
        else:
            lines.append("  • No se encontró ruta viable")
        lines.append("")
        lines.append("" + "═" * 80)
        return "\n".join(lines)

    def _ask_select_destination(self, hyper_label: str, candidates: list) -> str:
        """Muestra un diálogo modal para seleccionar el destino en la siguiente galaxia.

        Devuelve la label seleccionada o None si se cancela.
        """
        dlg = tk.Toplevel(self)
        dlg.title(f"Destino para salto desde {hyper_label}")
        dlg.geometry("360x300")
        dlg.transient(self)
        dlg.grab_set()

        tk.Label(dlg, text=f"Elige destino en la siguiente galaxia para {hyper_label}:", wraplength=340).pack(pady=8)
        listbox = tk.Listbox(dlg, selectmode='browse')
        for it in candidates:
            listbox.insert('end', it)
        listbox.pack(fill='both', expand=True, padx=8, pady=8)

        sel = {'choice': None}

        def on_ok():
            sel_idx = listbox.curselection()
            if sel_idx:
                sel['choice'] = listbox.get(sel_idx[0])
            dlg.destroy()

        def on_cancel():
            dlg.destroy()

        btnf = tk.Frame(dlg)
        btnf.pack(fill='x', padx=8, pady=6)
        ttk.Button(btnf, text='OK', command=on_ok).pack(side='left', expand=True, fill='x')
        ttk.Button(btnf, text='Cancelar', command=on_cancel).pack(side='left', expand=True, fill='x')

        self.wait_window(dlg)
        return sel['choice']

    def _on_calcular_optimizada(self):
        if not self.grafo:
            messagebox.showwarning("Atención", "Carga primero un JSON de constelaciones")
            return

        origen = self.combo_origen.get()
        if not origen:
            messagebox.showwarning("Atención", "Selecciona la estrella de origen")
            return

        try:
            salud = self.combo_salud.get()
            edad = float(self.entry_edad.get())
            energia = float(self.entry_energia.get())
            pasto = float(self.entry_pasto.get())
        except ValueError:
            messagebox.showerror("Error", "Verifica que edad, energía y pasto sean números válidos")
            return

        if propose_route is None:
            messagebox.showerror("Error", "El optimizador no está disponible (módulo faltante o error)")
            return

        # Build grafo compatible (labels)
        grafo = self.grafo

        # load original JSON data from the map if possible (we rely on constelaciones.json file)
        data = None
        try:
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            cand = os.path.join(repo_root, 'constelaciones.json')
            if os.path.exists(cand):
                with open(cand, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        except Exception:
            data = None

        if data is None:
            messagebox.showwarning('Aviso', 'No se pudo cargar constelaciones.json; se utilizarán valores por defecto')
            data = {'constellations': []}

        burro_init = {'salud': salud, 'edad': edad, 'energia': energia, 'pasto': pasto}

        res = propose_route(grafo, data, origen, burro_init, time_limit_seconds=3.0)

        # Simulación paso-a-paso para permitir pausa en hipergigantes
        pasos = res.get('pasos', [])
        ruta_actual = [origen]
        merged_final_route = None
        merged_final_res = None

        # limpiar y mostrar cabecera básica
        self.txt.delete('1.0', tk.END)
        self.txt.insert(tk.END, "══" + "═" * 78 + "\n")
        self.txt.insert(tk.END, "  Simulación paso a paso (pausa en hipergigantes)\n")
        self.txt.insert(tk.END, "══" + "═" * 78 + "\n\n")

        processed_hyper = False
        for idx, paso in enumerate(pasos, start=1):
            destino = paso.get('hacia')
            desde = paso.get('desde')
            vida = paso.get('tiempo_vida_restante')
            energia_despues = paso.get('energia_despues')
            pasto_rest = paso.get('pasto_restante')
            eaten = paso.get('eaten_kg', 0)
            estado_salud = paso.get('estado_salud', salud)

            ruta_actual.append(destino)

            # Mostrar el paso en el log
            if paso.get('jump_to'):
                line = f"{idx}. {desde} -> {destino} (dist {paso.get('distancia')}) -> JUMP to {paso.get('jump_to')} | Vida: {vida:.1f} | Pasto comido: {eaten}\n"
            else:
                line = f"{idx}. {desde} -> {destino} (dist {paso.get('distancia')}) | Vida: {vida:.1f} | Pasto comido: {eaten}\n"
            self.txt.insert(tk.END, line)
            self.txt.see(tk.END)

            # dibujar ruta parcial en el mapa
            try:
                if hasattr(self, 'mapa') and self.mapa is not None and hasattr(self.mapa, 'draw_route'):
                    try:
                        self.mapa.clear_route()
                        self.mapa.draw_route(ruta_actual)
                    except Exception:
                        pass
            except Exception:
                pass

            # Si es hipergigante, pausar y pedir destino
            if paso.get('hypergiant') and not processed_hyper:
                processed_hyper = True
                hyper_label = destino

                # encontrar metadatos de la estrella hyper
                star_meta = None
                for c in data.get('constellations', []):
                    for s in c.get('starts', []):
                        if s.get('label') == hyper_label:
                            star_meta = s
                            break
                    if star_meta:
                        break

                candidates = []
                if star_meta:
                    try:
                        origin_gal = int(star_meta.get('galaxy', -1))
                    except Exception:
                        origin_gal = -1
                    target_gal = origin_gal + 1
                    for c in data.get('constellations', []):
                        for s in c.get('starts', []):
                            try:
                                if int(s.get('galaxy', -1)) == target_gal:
                                    candidates.append(s.get('label'))
                            except Exception:
                                continue

                if not candidates:
                    self.txt.insert(tk.END, f"⚠️  No hay candidatos para salto desde {hyper_label} hacia la galaxia {origin_gal + 1}\n")
                    break

                choice = self._ask_select_destination(hyper_label, candidates)
                if not choice:
                    self.txt.insert(tk.END, "⏸️  Selección cancelada por el científico. Simulación detenida.\n")
                    break

                # Re-ejecutar optimizador desde la elección con el estado actual del burro
                burro_after = {'salud': estado_salud, 'edad': edad, 'energia': energia_despues, 'pasto': pasto_rest, 'tiempo_vida': vida}
                forced = {hyper_label: choice}
                self.txt.insert(tk.END, f"🔁  Recalculando ruta desde {choice} usando el estado actual del burro...\n")
                self.txt.see(tk.END)

                res2 = propose_route(grafo, data, choice, burro_after, time_limit_seconds=3.0, forced_jumps=forced)

                # Merge routes: ruta_actual contains hasta el hyper (incluye destino hyper), añadir choice y resto
                merged_final_route = ruta_actual + [choice] + res2.get('ruta', [])[1:]
                merged_final_res = res2
                break

        # Si hubo un cálculo posterior a la pausa, mostrar sus resultados combinados
        if merged_final_res is not None:
            texto2 = self._build_label_for_opt({
                'ruta': merged_final_route,
                'estrellas_visitadas': merged_final_res.get('estrellas_visitadas', 0) + len(ruta_actual) - 1,
                'energia_final': merged_final_res.get('energia_final'),
                'pasto_final': merged_final_res.get('pasto_final'),
                'tiempo_vida_final': merged_final_res.get('tiempo_vida_final'),
                'energia_inicial': energia,
                'pasto_inicial': pasto,
                'pasos': merged_final_res.get('pasos', [])
            })
            self.txt.insert(tk.END, "\n" + texto2)
            try:
                if hasattr(self, 'mapa') and self.mapa is not None:
                    try:
                        self.mapa.clear_route()
                        if hasattr(self.mapa, 'animate_route'):
                            self.mapa.animate_route(merged_final_route, step_delay_ms=450)
                        else:
                            self.mapa.draw_route(merged_final_route)
                    except Exception:
                        pass
            except Exception:
                pass
        else:
            # no hubo pausa/hyper o no se eligió destino: mostrar el resultado original
            texto = self._build_label_for_opt({
                'ruta': res.get('ruta'),
                'estrellas_visitadas': res.get('estrellas_visitadas'),
                'energia_final': res.get('energia_final'),
                'pasto_final': res.get('pasto_final'),
                'tiempo_vida_final': res.get('tiempo_vida_final'),
                'energia_inicial': energia,
                'pasto_inicial': pasto,
                'pasos': res.get('pasos', [])
            })
            self.txt.insert(tk.END, "\n" + texto)

        # Draw route on map if available
        try:
            if hasattr(self, 'mapa') and self.mapa is not None:
                ruta = res.get('ruta', [])
                if ruta:
                    try:
                        self.mapa.clear_route()
                        if hasattr(self.mapa, 'animate_route'):
                            self.mapa.animate_route(ruta, step_delay_ms=450)
                        else:
                            self.mapa.draw_route(ruta)
                    except Exception:
                        pass
        except Exception:
            pass

        # If burro died during the simulation, attempt to play a death sound
        try:
            tiempo_final = res.get('tiempo_vida_final', None)
            if tiempo_final is not None and float(tiempo_final) <= 0:
                # try a few candidate sound files in assets
                from pathlib import Path
                repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                candidates = [
                    os.path.join(repo_root, 'assets', 'muerto.wav'),
                    os.path.join(repo_root, 'assets', 'burrocantando2.wav'),
                    os.path.join(repo_root, 'assets', 'mala.jpg')
                ]
                played = False
                for c in candidates:
                    if Path(c).exists():
                        try:
                            if SoundHelper is not None:
                                SoundHelper.play_sound(c)
                                played = True
                                break
                        except Exception:
                            played = False
                if not played:
                    # fallback: insert a warning in the text area
                    self.txt.insert(tk.END, "\n⚰️  Atención: el burro ha muerto durante la ruta (no se pudo reproducir sonido).\n")
        except Exception:
            pass

