import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
import traceback

try:
    from components.mapa_widget import MapaWidget
except ImportError:
    from views.components.mapa_widget import MapaWidget

try:
    from components.panel_rutas import PanelRutas
except ImportError:
    from views.components.panel_rutas import PanelRutas

try:
    from components.panel_control import PanelControlCaminos
except ImportError:
    from views.components.panel_control import PanelControlCaminos

try:
    from views.windows.dialog_research_editor import ResearchEditor
except ImportError:
    try:
        from windows.dialog_research_editor import ResearchEditor
    except ImportError:
        ResearchEditor = None


class MainWindow(tk.Tk):
    def __init__(self, default_json=None):
        super().__init__()
        self.title("Burro Espacial - Centro de Control 🚀")
        self.geometry("1000x820")
        self.configure(bg="#0b0c10")

        # Guardar última ruta JSON cargada (para el panel de rutas)
        self.last_json_path = default_json

        # === Animación de aparición (fade-in) ===
        self.fade_in()

        # === Sección izquierda: Mapa de constelaciones ===
        self.mapa = MapaWidget(self, width=820, height=800)
        self.mapa.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        # === Panel derecho (controles) ===
        ctrl = tk.Frame(self, width=180, bg="#111")
        ctrl.pack(side="right", fill="y", padx=4, pady=4)

        # === Título decorativo ===
        lbl_title = tk.Label(
            ctrl,
            text="🛰️ Control del Burro",
            bg="#111", fg="#00eaff",
            font=("Orbitron", 13, "bold"),
            wraplength=160
        )
        lbl_title.pack(pady=(5, 10))

        # === Botones principales ===
        self.btn_load = ttk.Button(ctrl, text="Cargar JSON", command=self.on_load)
        self.btn_load.pack(fill="x", pady=6)

        self.btn_clear = ttk.Button(ctrl, text="Limpiar", command=self.mapa.clear)
        self.btn_clear.pack(fill="x", pady=6)

        self.btn_highlight = ttk.Button(ctrl, text="Resaltar Hipergigantes", command=self.highlight_hyper)
        self.btn_highlight.pack(fill="x", pady=6)

        self.btn_edit_research = ttk.Button(ctrl, text="Editar Investigación", command=self.on_edit_research)
        self.btn_edit_research.pack(fill="x", pady=6)
        # Botón para abrir el panel de cálculo de ruta
        self.btn_open_rutas = ttk.Button(ctrl, text="Calcular Ruta Óptima", command=self.on_open_panel_rutas)
        self.btn_open_rutas.pack(fill="x", pady=6)
        
        # Botón para gestionar caminos bloqueados
        self.btn_control_caminos = ttk.Button(ctrl, text="Gestionar Caminos 🚧", command=self.on_open_control_caminos)
        self.btn_control_caminos.pack(fill="x", pady=6)

        # === Estado ===
        self.status = tk.Label(
            ctrl, text="Lista para cargar constelaciones",
            wraplength=160, bg="#111", fg="white",
            font=("Arial", 9)
        )
        self.status.pack(fill="x", pady=8)

        # === Cargar JSON por defecto (si se pasa ruta) ===
        if default_json and os.path.exists(default_json):
            try:
                with open(default_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.mapa.load(data)
                self.status.config(text=f"Cargado: {os.path.basename(default_json)}")
                self.last_json_path = default_json
            except Exception as e:
                traceback.print_exc()
                messagebox.showerror("Error", f"No se pudo cargar JSON por defecto:\n{e}")

    # === Animación de aparición (fade-in suave) ===
    def fade_in(self):
        """Hace que la ventana aparezca progresivamente (como llegada al espacio)."""
        self.attributes("-alpha", 0.0)
        step = 0.05

        def animar():
            alpha = self.attributes("-alpha")
            if alpha < 1:
                self.attributes("-alpha", alpha + step)
                self.after(50, animar)

        animar()

    # === Cargar archivo JSON ===
    def on_load(self):
        path = filedialog.askopenfilename(title="Seleccionar JSON",
                                          filetypes=[("JSON", "*.json"), ("Todos los archivos", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.mapa.load(data)
            self.status.config(text=f"Cargado: {os.path.basename(path)}")
            self.last_json_path = path
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo cargar JSON:\n{e}")

    # === Resaltar estrellas hipergigantes ===
    def highlight_hyper(self):
        data = getattr(self.mapa, "data", None)
        if not data or "constellations" not in data:
            messagebox.showinfo("Info", "Carga primero un JSON con constelaciones")
            return

        const_data = data["constellations"]

        all_x = [s["coordenates"]["x"] for c in const_data for s in c.get("starts", [])]
        all_y = [s["coordenates"]["y"] for c in const_data for s in c.get("starts", [])]

        if not all_x or not all_y:
            return

        minx, maxx = min(all_x), max(all_x)
        miny, maxy = min(all_y), max(all_y)
        range_x = maxx - minx or 1
        range_y = maxy - miny or 1

        def to_canvas(x, y):
            cx = ((x - minx) / range_x) * (self.mapa.width - 60) + 30
            cy = ((y - miny) / range_y) * (self.mapa.height - 60) + 30
            return cx, cy

        for c in const_data:
            for s in c.get("starts", []):
                if s.get("hypergiant"):
                    x, y = s["coordenates"]["x"], s["coordenates"]["y"]
                    cx, cy = to_canvas(x, y)
                    r = max(3, s.get("radius", 0.5) * 6)
                    self.mapa.canvas.create_rectangle(cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6,
                                                      outline="yellow", width=3)

        self.status.config(text="Hipergigantes resaltadas 🌟")

    # === Abrir diálogo de investigación ===
    def on_edit_research(self):
        if ResearchEditor is None:
            messagebox.showerror('Error', 'Diálogo de edición no disponible')
            return
        data = getattr(self.mapa, 'data', None)
        if not data:
            messagebox.showinfo('Info', 'Carga primero un JSON con constelaciones')
            return
        dlg = ResearchEditor(self, data)
        dlg.grab_set()

    # === Abrir panel de cálculo de rutas ===
    def on_open_panel_rutas(self):
        top = tk.Toplevel(self)
        top.title("Ruta Óptima - Máximas estrellas")
        top.geometry("720x640")
        top.configure(bg="#0b0c10")

        panel = PanelRutas(top, bg="#0b0c10")
        panel.pack(fill="both", expand=True)

        # Si ya hay un JSON cargado, preparar el grafo
        if self.last_json_path and os.path.exists(self.last_json_path):
            try:
                panel.set_grafo_from_json(self.last_json_path)
            except Exception:
                pass

    # === Abrir panel de control de caminos ===
    def on_open_control_caminos(self):
        """Abre el panel para bloquear/habilitar caminos entre estrellas"""
        data = getattr(self.mapa, 'data', None)
        if not data:
            messagebox.showinfo('Info', 'Carga primero un JSON con constelaciones')
            return
        
        top = tk.Toplevel(self)
        top.title("Control de Caminos - Bloqueo/Habilitación")
        top.geometry("800x700")
        top.configure(bg="#0b0c10")

        panel = PanelControlCaminos(top, bg="#0b0c10")
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        # Cargar datos del JSON
        if self.last_json_path:
            panel.cargar_datos(self.last_json_path, data)
            
            # Callback para recargar el mapa cuando se bloqueen/habiliten caminos
            def on_cambio():
                try:
                    # Recargar el mapa con los datos actualizados
                    self.mapa.load(data)
                except Exception as e:
                    print(f"Error al recargar mapa: {e}")
            
            panel.set_on_cambio_callback(on_cambio)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
