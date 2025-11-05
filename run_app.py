"""Runner to start the application from the project root.

Usage:
  python run_app.py        # opens the GUI
  python run_app.py --test # runs headless checks (delegates to render_constelaciones --test)
"""
import sys
import os


if __name__ == '__main__':
    args = sys.argv[1:]
    if '--test' in args:
        # delegate to render_constelaciones test mode
        script = os.path.join(os.path.dirname(__file__), 'render_constelaciones.py')
        os.execv(sys.executable, [sys.executable, script, '--test'])
    else:
        # run main window
        try:
            from views.main_window import MainWindow
        except Exception:
            # fallback direct import
         from views.main_window import MainWindow

        # allow passing a JSON path as first argument: `python run_app.py path/to/file.json`
        json_path = None
        if len(args) >= 1 and args[0] != '--test':
            json_path = args[0]

        # pass default path into MainWindow so it can load during init
        default = None
        if json_path:
            default = json_path
        else:
            cand = os.path.join(os.path.dirname(__file__), 'constelaciones.json')
            if os.path.exists(cand):
                default = cand

        app = MainWindow(default_json=default)
        app.mainloop()
