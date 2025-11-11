import json
import os

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

    def dfs(actual, energia, pasto, visitadas):
        nonlocal mejor_ruta, max_estrellas
        if energia <= 0 or pasto <= 0:
            return
        if len(visitadas) > max_estrellas:
            mejor_ruta = visitadas.copy()
            max_estrellas = len(visitadas)

        for destino, distancia in grafo.get(actual, {}).items():
            if destino in visitadas:
                continue
            consumo_energia = distancia * 1.2
            consumo_pasto = distancia * 0.7
            nueva_energia = energia - consumo_energia
            nuevo_pasto = pasto - consumo_pasto
            if nueva_energia > 0 and nuevo_pasto > 0:
                dfs(destino, nueva_energia, nuevo_pasto, visitadas + [destino])

    dfs(estrella_origen, burroenergia, pasto_bodega, [estrella_origen])

    estado_final = estado_salud_por_energia(burroenergia - (100 - burroenergia))
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

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#0b0c10")

        self.grafo = {}

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

