from PyQt5 import QtWidgets, QtGui, QtCore, QtMultimedia
import sys, os

class Portada(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # === Ventana ===
        self.setWindowTitle("🚀 Burro Espacial 🚀")
        self.setFixedSize(1000, 700)
        self.setStyleSheet("background-color: black;")

        # === Fondo ===
        self.background = QtWidgets.QLabel(self)
        self.background.setGeometry(0, 0, 1000, 700)
        pixmap = QtGui.QPixmap("BurroEspacial/assets/por.jpg")
        pixmap = pixmap.scaled(950, 650, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.background.setPixmap(pixmap)
        self.background.setAlignment(QtCore.Qt.AlignCenter)
        self.background.setStyleSheet("border-radius: 20px; margin: 25px;")

        # === Título ===
        self.title = QtWidgets.QLabel("BURRO ESPACIAL", self)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setGeometry(0, 60, 1000, 100)
        self.title.setStyleSheet("""
            color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
            stop:0 #00fff7, stop:0.5 #ffffff, stop:1 #00ffea);
            font-family: Orbitron;
            font-size: 58px;
            font-weight: bold;
        """)

        # === Botón principal ===
        self.btn_iniciar = QtWidgets.QPushButton("🚀 INICIAR VIAJE", self)
        self.btn_iniciar.setGeometry(350, 480, 300, 90)
        self.btn_iniciar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_iniciar.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00111a, stop:1 #0077ff);
                color: white;
                font-family: Orbitron;
                font-size: 24px;
                font-weight: bold;
                border-radius: 18px;
                border: 2px solid #00eaff;
                padding: 10px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #00eaff;
                color: black;
            }
        """)
        self.btn_iniciar.clicked.connect(self.despegar)

        # === Texto de despegue (oculto al inicio) ===
        self.mensaje = QtWidgets.QLabel("", self)
        self.mensaje.setAlignment(QtCore.Qt.AlignCenter)
        self.mensaje.setGeometry(0, 600, 1000, 80)
        self.mensaje.setStyleSheet("""
            color: white;
            font-family: Orbitron;
            font-size: 28px;
        """)

        # === Efecto parpadeo del botón ===
        self.timer_color = QtCore.QTimer()
        self.timer_color.timeout.connect(self.cambiar_color)
        self.timer_color.start(500)
        self.toggle = True

        # === Cargar sonido si existe ===
        self.sound_effect = None
        if os.path.exists("assets/despegue.mp3"):
            url = QtCore.QUrl.fromLocalFile(os.path.abspath("assets/despegue.mp3"))
            self.sound_effect = QtMultimedia.QMediaPlayer()
            self.sound_effect.setMedia(QtMultimedia.QMediaContent(url))

    # === Parpadeo dinámico ===
    def cambiar_color(self):
        if self.toggle:
            color = "#00eaff"
            text = "black"
        else:
            color = "#00111a"
            text = "white"

        self.btn_iniciar.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text};
                font-family: Orbitron;
                font-size: 24px;
                font-weight: bold;
                border-radius: 18px;
                border: 2px solid #00eaff;
                padding: 10px;
            }}
        """)
        self.toggle = not self.toggle

    # === Cuando se hace clic ===
    def despegar(self):
        self.timer_color.stop()

        # sonido
        if self.sound_effect:
            self.sound_effect.play()

        # mostrar texto
        self.mensaje.setText("🚀 Despegando hacia las constelaciones...")
        self.animar_texto()

        # animación de fade total
        self.fade = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.fade.setDuration(3000)
        self.fade.setStartValue(1)
        self.fade.setEndValue(0)
        self.fade.finished.connect(self.ir_a_main_window)
        self.fade.start()

    def animar_texto(self):
        self.anim = QtCore.QPropertyAnimation(self.mensaje, b"windowOpacity")
        self.anim.setDuration(1000)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setLoopCount(-1)
        self.anim.start()

    def ir_a_main_window(self):
        """Abre la interfaz principal (window.py)"""
        from views.windows.main_window import MainWindow
        self.close()
        self.main_window = MainWindow()
        self.main_window.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    ventana = Portada()
    ventana.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
