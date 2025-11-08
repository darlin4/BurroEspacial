from PyQt5 import QtWidgets, QtGui, QtCore
import sys, os, threading
from playsound import playsound

def play_sound_async(path):
    """Reproduce un sonido en segundo plano."""
    if os.path.exists(path):
        threading.Thread(target=playsound, args=(path,), daemon=True).start()
    else:
        print(f"⚠️ No se encontró el archivo: {path}")

class Portada(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # === Ventana principal ===
        self.setWindowTitle("🚀 Burro Espacial 🚀")
        self.setFixedSize(1000, 700)
        self.setStyleSheet("background-color: black;")

        # === Imagen de fondo ===
        self.background = QtWidgets.QLabel(self)
        self.background.setGeometry(0, 0, 1000, 700)
        pixmap = QtGui.QPixmap("assets/por.jpg")
        pixmap = pixmap.scaled(950, 650, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.background.setPixmap(pixmap)
        self.background.setAlignment(QtCore.Qt.AlignCenter)

        # === Título ===
        self.title = QtWidgets.QLabel("🌌 BURRO ESPACIAL 🌌", self)
        self.title.setGeometry(0, 80, 1000, 100)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet("""
            color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
            stop:0 #00fff7, stop:0.5 #ffffff, stop:1 #00ffea);
            font-family: Orbitron;
            font-size: 58px;
            font-weight: bold;
            letter-spacing: 3px;
        """)

        # === Botón principal ===
        self.btn_iniciar = QtWidgets.QPushButton("🌠 DESPEGAMOS A LA LUNA 🌠", self)
        self.btn_iniciar.setGeometry(325, 480, 350, 90)
        self.btn_iniciar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_iniciar.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00111a, stop:1 #0077ff);
                color: white;
                font-family: Orbitron;
                font-size: 22px;
                font-weight: bold;
                border-radius: 20px;
                border: 2px solid #00eaff;
                padding: 10px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #00eaff;
                color: black;
                transform: scale(1.05);
            }
        """)
        self.btn_iniciar.clicked.connect(self.despegar)

        # === Texto de mensaje ===
        self.mensaje = QtWidgets.QLabel("", self)
        self.mensaje.setGeometry(0, 600, 1000, 80)
        self.mensaje.setAlignment(QtCore.Qt.AlignCenter)
        self.mensaje.setStyleSheet("color: white; font-family: Orbitron; font-size: 26px;")

        # === Parpadeo dinámico del botón ===
        self.timer_color = QtCore.QTimer()
        self.timer_color.timeout.connect(self.cambiar_color)
        self.timer_color.start(600)
        self.toggle = True

        # === Ruta del audio ===
        self.audio_path = "assets/burrocantando2.wav"

        # Mantener referencias para que no las borre el GC
        self.fade = None
        self.anim_texto = None

    def cambiar_color(self):
        """Efecto parpadeo del botón."""
        color = "#00eaff" if self.toggle else "#00111a"
        text = "black" if self.toggle else "white"
        self.btn_iniciar.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text};
                font-family: Orbitron;
                font-size: 22px;
                font-weight: bold;
                border-radius: 20px;
                border: 2px solid #00eaff;
                padding: 10px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: #00eaff;
                color: black;
                transform: scale(1.05);
            }}
        """)
        self.toggle = not self.toggle

    def despegar(self):
        """Acción del botón: reproduce sonido y transiciona."""
        self.timer_color.stop()
        play_sound_async(self.audio_path)
        self.mensaje.setText("🚀 Despegando hacia las constelaciones... 🌙")
        self.animar_texto()

        # 💡 Mantener referencia a la animación para que no se destruya
        self.fade = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.fade.setDuration(4000)
        self.fade.setStartValue(1)
        self.fade.setEndValue(0)
        self.fade.finished.connect(self.ir_a_main_window)
        self.fade.start()

    def animar_texto(self):
        """Animación del texto de despegue (parpadeo suave)."""
        self.anim_texto = QtCore.QPropertyAnimation(self.mensaje, b"windowOpacity")
        self.anim_texto.setDuration(1000)
        self.anim_texto.setStartValue(0)
        self.anim_texto.setEndValue(1)
        self.anim_texto.setLoopCount(-1)
        self.anim_texto.start()

    def ir_a_main_window(self):
        """Abre la siguiente ventana."""
        from views.windows.main_window import MainWindow  # Ajusta ruta si difiere
        self.close()
        self.main_window = MainWindow()
        self.main_window.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    ventana = Portada()
    ventana.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
