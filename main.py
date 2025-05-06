import json, os, sys
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt
import ctypes
from ctypes import wintypes

dwmapi = ctypes.windll.dwmapi
DWMWA_CAPTION_COLOR = 35
WM_SYSCOMMAND = 0x0112
SC_MINIMIZE = 0xF020

def set_title_bar_color(hwnd, color):
    color = wintypes.DWORD(color)
    hwnd = wintypes.HWND(hwnd)
    dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_CAPTION_COLOR, ctypes.byref(color), ctypes.sizeof(color))


class reWord(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("reWord.ui", self)
        self.setWindowTitle("reWord")
        hwnd = int(self.winId())
        set_title_bar_color(hwnd, 0x00050505)

        # Cards parameters
        self.widget_width = 185
        self.widget_height = 185
        self.widgets = []

        self.relayout_widgets()

        self.newSetBtn.clicked.connect(lambda: (self.add_card(), self.relayout_widgets()))

    def add_card(self):
        # Maximum size = 30 chars
        w = WCard("Food", "🫦 Norwegian")
        self.widgets.append(w)
        

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.relayout_widgets()
        
    def relayout_widgets(self):
        while self.mainPageGrid.count():
            item = self.mainPageGrid.takeAt(0)
            if w := item.widget():
                self.mainPageGrid.removeWidget(w)

        self.mainPageGrid.setContentsMargins(0,0,0,0)
        self.mainPageGrid.setHorizontalSpacing(10)
        self.mainPageGrid.setVerticalSpacing(10)

        margins = self.mainPageGrid.contentsMargins()
        spacing = self.mainPageGrid.horizontalSpacing()
        avail_w = self.scrollArea.viewport().width() - (margins.left() + margins.right())
        unit = self.widget_width + spacing
        columns = max(1, (avail_w + spacing) // unit)

        for idx, w in enumerate(self.widgets):
            row, col = divmod(idx, columns)
            self.mainPageGrid.addWidget(w, row, col, alignment=Qt.AlignTop|Qt.AlignLeft)

        rows = (len(self.widgets)-1) // columns
        for c in range(columns+1):
            self.mainPageGrid.setColumnStretch(c, 0)
        for r in range(rows+2):
            self.mainPageGrid.setRowStretch(r, 0)
        self.mainPageGrid.setColumnStretch(columns, 1)
        self.mainPageGrid.setRowStretch(rows+1, 1)


class WCard(QtWidgets.QWidget):
    def __init__(self, title: str, tag: str):
        super().__init__()
        self.setFixedSize(185, 185)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #1b1b1b; border-radius: 7px; border-color: #FF2C55; border: 1.5px solid #FF2C55;")

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(12,12,12,12)
        vbox.setSpacing(8)

        title_lbl = QtWidgets.QLabel(title, self)
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet("color: white; font-size: 28px; border: none;")
        vbox.addWidget(title_lbl)

        tag_lbl = QtWidgets.QLabel(tag, self)
        tag_lbl.setStyleSheet("color: #797979; font-size: 14px; border: none;")
        vbox.addWidget(tag_lbl)

        word_counter = "0 word pairs" # CHANGE ME LATER
        word_counter_lbl = QtWidgets.QLabel(word_counter, self)
        word_counter_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        word_counter_lbl.setStyleSheet("color: #797979; font-size: 14px; border: none;")
        vbox.addWidget(word_counter_lbl)

        

class Files:
    def create(name):
        open(name, "w", encoding="utf-8").close()


    def delete(name):
        if os.path.exists(name):
            os.remove(name)
        else:
            # Later will be logged
            print(f"Could not delete '{name}': file isn't found.")


    def read(name):
        with open(name, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
        

    def record(name, data):
        with open(name, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)


    def get_all_ids(file):
        try:
            with open(file, 'r', encoding='utf-8') as file:
                words = json.load(file)

            ids = [word.get('id') for word in words if "id" in word]
            return ids
        
        except FileNotFoundError: 
            print("Could not get all ID's: file not found.")
            return []
        
        except json.JSONDecodeError:
            print("Could not get all ID's: file corrupted or empty.")
            return []
        
    
    def delete_id(file_p, id):
        try:
            with open(file_p, "r", encoding="utf-8") as file:
                words = json.load(file)

            words = [word for word in words if word.get('id') != id]

            for new_id, word in enumerate(words, start=1):
                word['id'] = new_id

            with open(file_p, "w", encoding="utf-8") as file:
                json.dump(words, file, ensure_ascii=False, indent=2)

        except FileNotFoundError: 
            print("Could not get all ID's: file not found.")
        
        except json.JSONDecodeError:
            print("Could not get all ID's: file corrupted or empty.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = reWord()
    window.show()
    sys.exit(app.exec_())
