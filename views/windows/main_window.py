"""
Ventana principal del sistema de navegación espacial NASA.
"""

# Aquí iría la implementación de MainWindow
# - Ventana principal de la aplicación
# - Menús y barras de herramientas
# - Layout principal con paneles
# - Coordinación de componentes
# BurroEspacial/views/windows/window.py
from PyQt5 import QtWidgets, QtGui, QtCore

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Centro de Control - Burro Espacial 🛰️")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #0b0c10; color: white;")

        # === Label temporal (de prueba) ===
        self.label = QtWidgets.QLabel("Bienvenido al viaje del burro espacial 🌌", self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setGeometry(0, 0, 1200, 800)
        self.label.setStyleSheet("""
            font-family: Orbitron;
            font-size: 30px;
            color: #00eaff;
        """)
