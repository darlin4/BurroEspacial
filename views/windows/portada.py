from PyQt5 import QtWidgets, QtGui, QtCore
import sys

class Portada(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("🚀 Burro Espacial 🚀")
        self.setFixedSize(900, 600)

        # === Fondo ===
        self.background = QtWidgets.QLabel(self)
        self.background.setGeometry(0, 0, 900, 600)
        pixmap = QtGui.QPixmap("BurroEspacial/assets/por.jpg")
        pixmap = pixmap.scaled(850, 550, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.background.setPixmap(pixmap)
        self.background.setAlignment(QtCore.Qt.AlignCenter)
        self.background.setStyleSheet("border-radius: 15px; margin: 25px;")

        # === Texto principal ===
        self.title = QtWidgets.QLabel("BURRO ESPACIAL", self)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setGeometry(0, 50, 900, 100)
        self.title.setStyleSheet("""
            color: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:0, 
                stop:0 #00fff7, stop:0.5 #ffffff, stop:1 #00ffea);
            font-family: Orbitron;
            font-size: 54px;
            font-weight: bold;
            text-shadow: 0 0 25px #00fff7;
        """)

        # === Botón de inicio ===
        self.btn_iniciar = QtWidgets.QPushButton("🚀 INICIAR VIAJE", self)
        self.btn_iniciar.setGeometry(300, 400, 300, 80)
        self.btn_iniciar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_iniciar.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #0f0f0f, stop:1 #0077ff);
                color: white;
                font-family: Orbitron;
                font-size: 22px;
                font-weight: bold;
                border-radius: 15px;
                border: 2px solid #00eaff;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #00eaff;
                color: black;
            }
        """)
        self.btn_iniciar.clicked.connect(self.start_animation)

        # === Animación del título (brillo suave) ===
        self.animation = QtCore.QPropertyAnimation(self.title, b"windowOpacity")
        self.animation.setDuration(3000)
        self.animation.setStartValue(0.3)
        self.animation.setEndValue(1.0)
        self.animation.setLoopCount(-1)
        self.animation.start()

    def start_animation(self):
        """Efecto de salida tipo 'despegue' antes de pasar al grafo o video"""
        self.fade = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.fade.setDuration(1000)
        self.fade.setStartValue(1)
        self.fade.setEndValue(0)
        self.fade.finished.connect(self.start_journey)
        self.fade.start()

    def start_journey(self):
        print("🚀 Despegando hacia las constelaciones...")
        self.close()
        # Aquí luego conectas con la ventana del grafo o video

def main():
    app = QtWidgets.QApplication(sys.argv)
    ventana = Portada()
    ventana.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
