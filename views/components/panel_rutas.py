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
        "pasto_inicial": pasto_bodega
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
        except Exception as e:
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

        res = ruta_maxima(origen, salud, edad, energia, pasto, self.grafo)

        # Mostrar resultados
        self.txt.delete("1.0", tk.END)
        self.txt.insert(tk.END, "═" * 70 + "\n")
        self.txt.insert(tk.END, "RUTA CALCULADA (máximas estrellas por condiciones iniciales)\n")
        self.txt.insert(tk.END, "═" * 70 + "\n\n")
        self.txt.insert(tk.END, f"Origen: {origen}\n")
        self.txt.insert(tk.END, f"Estrellas visitadas: {res['estrellas_visitadas']}\n")
        self.txt.insert(tk.END, f"Ruta: {' -> '.join(res['ruta']) if res['ruta'] else 'Ninguna'}\n")
        self.txt.insert(tk.END, f"Estado final (aprox.): {res['estado_final']}\n")
        self.txt.insert(tk.END, f"Energía inicial: {res['energia_inicial']}% | Pasto inicial: {res['pasto_inicial']} kg\n")
        self.txt.insert(tk.END, "\n" + "─" * 70 + "\n")

