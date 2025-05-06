import json, os, sys, random
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt, QRegExp
import ctypes
from ctypes import wintypes
from PyQt5.QtGui import QRegExpValidator


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
        
        regexp = QRegExp(r"[A-Za-zА-Яа-я0-9 _-]+")
        validator = QRegExpValidator(regexp)

        self.pages.setCurrentWidget(self.mainPage)
        self.newSetBtn.clicked.connect(lambda: (self.new_set(), self.relayout_widgets()))
        self.mainPageBtn.clicked.connect(lambda: (self.pages.setCurrentWidget(self.mainPage), self.relayout_widgets()))

        self.newSetEdit.setValidator(validator)
        self.tagEdit.setValidator(validator)
        self.newSetEdit.returnPressed.connect(lambda: self.tagEdit.setFocus())
        self.tagEdit.returnPressed.connect(self.createSetBtn.click)
        self.createSetBtn.clicked.connect(self.create_set)

    def new_set(self):
        self.newSetEdit.clear()
        self.tagEdit.clear()
        self.pages.setCurrentWidget(self.newSetPage)
        self.newSetEdit.setFocus()


    def create_set(self):
        set_name = self.newSetEdit.text()
        if not set_name:
            self.create_warning_box("Could not create a set", "Title shouldn't be empty.")
            return
        tag_name = self.tagEdit.text()

        # Maximum size = 30 chars
        w = WCard(set_name, tag_name, parent=self)
        self.widgets.append(w)
        self.pages.setCurrentWidget(self.mainPage)
        self.relayout_widgets()

    def create_warning_box(self, title, desc):
        box = QtWidgets.QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(desc)
        box.setIcon(QtWidgets.QMessageBox.Warning)
        box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        box.setStyleSheet("""
            QMessageBox {
                background-color: #111;
                border: none;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #222;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #FF2C55;
                color: black;
            }
        """)
        box.exec_()

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

    def remove_card(self, card_widget):
        box = QtWidgets.QMessageBox(self)
        box.setWindowTitle("Delete the card?")
        box.setText("Do you really want to delete the card?")
        box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        box.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        box.setStyleSheet("""
            QMessageBox {
                background-color: #111;
                border: none;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #222;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #FF2C55;
                color: black;
            }
        """)
        answer = box.exec_()
        if answer == QtWidgets.QMessageBox.Yes:
            
            self.widgets.remove(card_widget)
            card_widget.setParent(None)
            self.relayout_widgets()


class WCard(QtWidgets.QWidget):
    def __init__(self, title: str, tag: str, parent=None):
        super().__init__(parent)
        self.owner = parent
        self.setFixedSize(185, 185)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet("""QWidget{
                           background-color: #1b1b1b; 
                           border-radius: 7px; 
                           border: 1.5px solid #FF2C55;
                           }

                           QWidget:hover {
                           background-color: #2D2D2D;
                           }
                           """)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(12,12,12,12)
        vbox.setSpacing(8)

        title_lbl = QtWidgets.QLabel(title, self)
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet("background-color: transparent; color: white; font-size: 28px; border: none;")
        vbox.addWidget(title_lbl)

        tag_lbl = QtWidgets.QLabel(tag, self)
        tag_lbl.setStyleSheet("background-color: transparent; color: #797979; font-size: 14px; border: none;")
        vbox.addWidget(tag_lbl)

        random_ch = ['0 word pairs', '21 word pairs', '13 word pairs', '312 word pairs']
        word_counter = random.choice(random_ch) # CHANGE ME LATER
        word_counter_lbl = QtWidgets.QLabel(word_counter, self)
        word_counter_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        word_counter_lbl.setStyleSheet("background-color: transparent; color: #797979; font-size: 14px; border: none;")
        vbox.addWidget(word_counter_lbl)

    def open_context_menu(self, position):
        menu = QtWidgets.QMenu(self)

        menu.setStyleSheet("""
            QMenu {
                background-color: #050505;
                color: white;
                border: none;
            }
            QMenu::item {
                padding: 6px 20px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #C41E3D;
                color: black;
            }
        """)

        action_delete = menu.addAction("❌ Delete")

        action = menu.exec_(self.mapToGlobal(position))

        if action == action_delete:
            if self.owner:
                self.owner.remove_card(self)

        

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
