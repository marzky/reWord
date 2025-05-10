import sys
from PyQt5 import QtWidgets
from app.reword import reWord

        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = reWord()
    window.show()
    sys.exit(app.exec_())
