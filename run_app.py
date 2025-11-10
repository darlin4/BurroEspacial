"""
Runner para iniciar la aplicación desde la raíz del proyecto.

Uso:
  python run_app.py         # abre la GUI (Portada PyQt5 -> MainWindow Tkinter)
  python run_app.py --test  # ejecuta pruebas en modo headless (delegado a render_constelaciones --test)
"""
import sys
import os
from views.components.panel_rutas import ruta_maxima, cargar_grafo_desde_json


if __name__ == '__main__':
    args = sys.argv[1:]
    if '--test' in args:
        # Modo prueba: delegar a render_constelaciones
        script = os.path.join(os.path.dirname(__file__), 'render_constelaciones.py')
        os.execv(sys.executable, [sys.executable, script, '--test'])
    else:
        # === Lanzar portada de PyQt5 ===
        from PyQt5 import QtWidgets
        from views.windows.portada import Portada

        app = QtWidgets.QApplication(sys.argv)
        portada = Portada()

        def lanzar_tkinter():
            """Cierra PyQt5 y abre la interfaz Tkinter."""
            portada.close()
            app.quit()
            
            # Importar y ejecutar MainWindow Tkinter
            from views.windows.main_window import MainWindow
            
            # Buscar archivo JSON por defecto
            default = None
            cand = os.path.join(os.path.dirname(__file__), 'constelaciones.json')
            if os.path.exists(cand):
                default = cand
            
            main_window = MainWindow(default_json=default)
            main_window.mainloop()

        # Sobrescribir el método de cambio de ventana
        portada.ir_a_main_window = lanzar_tkinter

        portada.show()
        sys.exit(app.exec_())
