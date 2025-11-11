import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
import sys
import traceback

# Asegurar que el proyecto raíz esté en sys.path para permitir `import views.*` al ejecutar este archivo directamente
_this_dir = os.path.dirname(__file__)
_project_root = os.path.abspath(os.path.join(_this_dir, '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from components.mapa_widget import MapaWidget
except ImportError:
    from views.components.mapa_widget import MapaWidget

# Paneles adicionales
try:
    from views.components.panel_calculo_ruta import PanelCalculoRuta
except Exception:
    PanelCalculoRuta = None

try:
    from views.components.panel_control import PanelControlCaminos
except Exception:
    PanelControlCaminos = None

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

        # === Nuevos botones: Ruta máxima y Gestión de caminos ===
        self.btn_ruta = ttk.Button(ctrl, text="Ruta máxima", command=self.abrir_calculadora_rutas)
        self.btn_ruta.pack(fill="x", pady=6)

        self.btn_caminos = ttk.Button(ctrl, text="Gestionar Caminos", command=self.abrir_control_caminos)
        self.btn_caminos.pack(fill="x", pady=6)

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
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo cargar JSON:\n{e}")

    # === Proveedor de grafo (desde JSON cargado) ===
    def _grafo_desde_cargado(self):
        data = getattr(self.mapa, 'data', None)
        grafo = {}
        if not data or 'constellations' not in data:
            return grafo
        consts = data['constellations']
        # construir índice id -> label
        id_to_label = {}
        for c in consts:
            for s in c.get('starts', []):
                id_to_label[s.get('id')] = s.get('label')
        # armar grafo
        for c in consts:
            for s in c.get('starts', []):
                origen = s.get('label')
                grafo.setdefault(origen, {})
                for link in s.get('linkedTo', []):
                    if link.get('blocked', False):
                        continue
                    destino_nombre = id_to_label.get(link.get('starId'))
                    if destino_nombre:
                        grafo[origen][destino_nombre] = link.get('distance', 0)
        return grafo

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
        # callback para notificar cambios en los parámetros de investigación
        def _on_research_change():
            try:
                # si el panel de rutas está abierto, recargar grafo desde datos en memoria
                if hasattr(self, 'panel_rutas') and self.panel_rutas is not None:
                    try:
                        self.panel_rutas.set_grafo_from_data(self.mapa.data)
                    except Exception:
                        pass
            except Exception:
                pass

        dlg = ResearchEditor(self, data, on_change=_on_research_change)
        dlg.grab_set()

    # === Abrir calculadora de rutas ===
    def abrir_calculadora_rutas(self):
        if PanelCalculoRuta is None:
            messagebox.showerror('Error', 'Panel de cálculo de ruta no disponible')
            return
        data = getattr(self.mapa, 'data', None)
        if not data:
            messagebox.showinfo('Info', 'Carga primero un JSON con constelaciones')
            return
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

    # === Abrir gestión de caminos ===
    def abrir_control_caminos(self):
        if PanelControlCaminos is None:
            messagebox.showerror('Error', 'Panel de gestión de caminos no disponible')
            return
        data = getattr(self.mapa, 'data', None)
        if not data:
            messagebox.showinfo('Info', 'Carga primero un JSON con constelaciones')
            return
        def on_change():
            # Redibujar mapa con el mismo data modificado (respeta bloqueos)
            self.mapa.load(self.mapa.data)
        top = tk.Toplevel(self)
        top.title('Bloquear/Habilitar caminos')
        top.geometry('720x520')
        panel = PanelControlCaminos(top, get_data=lambda: getattr(self.mapa, 'data', None), on_change=on_change)
        panel.pack(fill='both', expand=True)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
