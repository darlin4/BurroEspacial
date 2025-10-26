from PyQt5 import QtWidgets
import sys
from views.windows.portada import Portada

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana = Portada()
    ventana.show()
    sys.exit(app.exec_())
