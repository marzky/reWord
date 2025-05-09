import json, os, sys, random, glob
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt, QRegExp, QTimer
from PyQt5.QtWidgets import QStyledItemDelegate, QStyle
import ctypes
from datetime import datetime
from ctypes import wintypes
from PyQt5.QtGui import QRegExpValidator, QKeySequence


dwmapi = ctypes.windll.dwmapi
DWMWA_CAPTION_COLOR = 35
WM_SYSCOMMAND = 0x0112
SC_MINIMIZE = 0xF020

def set_title_bar_color(hwnd, color):
    color = wintypes.DWORD(color)
    hwnd = wintypes.HWND(hwnd)
    dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_CAPTION_COLOR, ctypes.byref(color), ctypes.sizeof(color))

class CleanNavigationDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.state &= ~QStyle.State_HasFocus

    def eventFilter(self, editor, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() in (Qt.Key_Return, Qt.Key_Enter):
            table = editor.parent().parent()
            row = table.currentRow()
            col = table.currentColumn()

            if col == 0:
                QtCore.QTimer.singleShot(0, lambda: table.setCurrentCell(row, 1))
                QtCore.QTimer.singleShot(0, lambda: table.editItem(table.item(row, 1)))
            else:
                next_row = row + 1
                if next_row < table.rowCount():
                    QtCore.QTimer.singleShot(0, lambda: table.setCurrentCell(next_row, 0))
                    QtCore.QTimer.singleShot(0, lambda: table.editItem(table.item(next_row, 0)))

            return True

        return super().eventFilter(editor, event)

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

        self.load_all_sets()

        self.filtering_mode = 'Date' # 'date', 'title', 'tag', 'group'
        self.sort_order = 'asc' # 'asc', 'desc'

        regexp = QRegExp(r"[A-Za-zА-Яа-я0-9 _-]+")
        validator = QRegExpValidator(regexp)

        new_set_shortcut = QtWidgets.QShortcut(QKeySequence("Ctrl+N"), self)
        new_set_shortcut.activated.connect(self.new_set)

        self.pages.setCurrentWidget(self.mainPage)
        self.newSetBtn.clicked.connect(lambda: (self.new_set(), self.relayout_widgets()))
        self.cancelBtn.clicked.connect(lambda: self.pages.setCurrentWidget(self.mainPage))
        self.mainPageBtn.clicked.connect(lambda: (self.pages.setCurrentWidget(self.mainPage), self.filtering_widgets()))

        self.newSetEdit.setValidator(validator)
        self.tagEdit.setValidator(validator)
        self.newSetEdit.returnPressed.connect(lambda: self.tagEdit.setFocus())
        self.tagEdit.returnPressed.connect(self.createSetBtn.click)
        self.createSetBtn.clicked.connect(self.create_set)

        self.filter_modes = ['Date', 'Title', 'Tag', 'Group']
        self.filterBox.addItems(self.filter_modes)
        self.filterBox.currentIndexChanged[int].connect(self.on_filter_changed)
        self.ascBtn.clicked.connect(lambda: self.on_sort_order_changed("asc"))
        self.descBtn.clicked.connect(lambda: self.on_sort_order_changed("desc"))

        self.setEditorTable = QtWidgets.QTableWidget()
        self.setEditorTable.setColumnCount(2)
        self.setEditorTable.setHorizontalHeaderLabels(["Word", "Translation"])
        self.setEditorLayout.addWidget(self.setEditorTable)
        self.setEditorTable.itemChanged.connect(self.check_for_auto_row_add)
        
        QTimer.singleShot(0, self.filtering_widgets)

    def load_all_sets(self):
        cards_dir = os.path.join(os.getcwd(), "cards")
        os.makedirs(cards_dir, exist_ok=True)

        for path in glob.glob(os.path.join(cards_dir, "*.json")):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                title = data.get("title", "")
                tag   = data.get("tag", "")
    
                if title:
                    tag = tag or "General"
                    word_count = len(data.get("words", []))
                    card = WCard(title, tag, word_count=word_count, parent=self)
                    self.widgets.append(card)
            except Exception as e:
                print(f"Could not load {path!r}: {e}")

    def new_set(self):
        self.newSetEdit.clear()
        self.tagEdit.clear()
        self.pages.setCurrentWidget(self.newSetPage)
        self.newSetEdit.setFocus()

    def on_filter_changed(self, index: int):
        if 0 <= index < len(self.filter_modes):
            self.filtering_mode = self.filter_modes[index]
        self.filtering_widgets()

    def on_sort_order_changed(self, order):
        self.sort_order = order
        self.filtering_widgets()

    def create_set(self):
        set_name = self.newSetEdit.text()
        if not set_name:
            self.create_warning_box("Could not create a set", "Title shouldn't be empty.")
            return
        tag_name = self.tagEdit.text()
        if not tag_name:
            tag_name = "General"

        if not Files.exists(set_name):
            Files.create(f"{set_name}")
            data = {
                "title": set_name,
                "tag": tag_name,
                "words": []
                }
            Files.record(set_name, data)

            # Maximum size = 30 chars
            w = WCard(set_name, tag_name, parent=self)
            self.widgets.insert(0, w)
            self.pages.setCurrentWidget(self.mainPage)
            self.relayout_widgets()
        else:
            self.create_warning_box("Could not create a set", "Set title is already in Cards directory. Please, change the title.")
            return

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

    def filtering_widgets(self):
        if self.filtering_mode == 'Title':
            self.widgets.sort(
                key=lambda w: w.title_lbl.text().lower(),
                reverse=(self.sort_order == 'desc')
            )
        elif self.filtering_mode == 'Date':
            self.widgets.sort(
                key=lambda w: Files.last_modified(w.title_lbl.text()),
                reverse=(self.sort_order == 'asc')  
            )
        elif self.filtering_mode == 'Tag':
            self.widgets.sort(
                key=lambda w: w.tag_lbl.text().lower(),
                reverse=(self.sort_order == 'desc')
            )
        else:
            print("Not implemented")

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
        box.setText(f"Do you really want to delete the card '{card_widget.title_lbl.text()}'?\nAll the information about the card and .json file will be deleted too.")
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
            Files.delete(card_widget.title_lbl.text())

    def open_set_editor(self, title: str):
        self.current_editing_title = title
        self.pages.setCurrentWidget(self.setEditor)

        self.setEditorTable.blockSignals(True)

        self.setEditorTable.clear()
        self.setEditorTable.setColumnCount(2)
        self.setEditorTable.setHorizontalHeaderLabels(["Word", "Translation"])
        self.setEditorTable.setRowCount(0)
        self.setEditorTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        delegate = CleanNavigationDelegate(self.setEditorTable)
        self.setEditorTable.setItemDelegate(delegate)
        self.setEditorTable.setItemDelegate(delegate)
        self.setEditorTable.setStyleSheet("""
                                    QTableWidget {
                                        background-color: #0D0D0D;
                                        color: white;
                                        font: 15px "Funnel Sans Light";
                                        gridline-color: #333333;
                                        selection-background-color: #FF2C55;
                                        selection-color: black;
                                        border: none;
                                    }
                                    QTableCornerButton::section {
                                        background-color: #0D0D0D;
                                        border: none;
                                    }
                                          
                                    QTableWidget QLineEdit {
                                        background-color: #1B1B1B;
                                        color: white;
                                        border: none;
                                        outline: none;
                                        selection-background-color: #FF2C55;
                                        selection-color: black;
                                        font: 15px "Funnel Sans Light";
                                    }
                                          
                                    QTableView::item:focus {
                                        outline: none;
                                        border: none;
                                    }

                                    QHeaderView::section {
                                        background-color: #2D2D2D;
                                        color: white;
                                        font: bold 14px "Funnel Sans";
                                        padding: 6px;
                                        border: none;
                                    }

                                    QTableWidget::item {
                                        padding: 6px;
                                        border: none;
                                        color: white;
                                    }

                                    QTableWidget::item:selected {
                                        border: 1.5px solid #FF2C55;
                                    }

                                    QScrollBar:vertical {
                                        background-color: #0D0D0D;
                                        width: 8px;
                                        margin: 0px;
                                    }

                                    QScrollBar::handle:vertical {
                                        background-color: #444;            
                                        border-radius: 4px;
                                        min-height: 25px;
                                    }

                                    QScrollBar::handle:vertical:hover {
                                        background-color: #666;
                                    }

                                    QScrollBar::add-line:vertical,
                                    QScrollBar::sub-line:vertical {
                                        height: 0px;
                                    }

                                    QScrollBar::add-page:vertical,
                                    QScrollBar::sub-page:vertical {
                                        background: none;
                                    }
                                """)

        if not Files.exists(title):
            self.create_warning_box("Error", f"Set '{title}' not found.")
            return

        data = Files.read(title)
        words = data.get("words", [])

        for word in words:
            self._add_editor_row(word.get("word", ""), word.get("translation", ""))

        if not words:
            self._add_editor_row("", "")
        else: 
            self._add_editor_row("", "")

        self.setEditorTable.blockSignals(False)


        last_row = self.setEditorTable.rowCount() - 1
        if last_row >= 0:
            self.setEditorTable.setCurrentCell(last_row, 0)
            self.setEditorTable.editItem(self.setEditorTable.item(last_row, 0))

    def _add_editor_row(self, word: str, translation: str):
        row = self.setEditorTable.rowCount()
        self.setEditorTable.insertRow(row)
        self.setEditorTable.setItem(row, 0, QtWidgets.QTableWidgetItem(word))
        self.setEditorTable.setItem(row, 1, QtWidgets.QTableWidgetItem(translation))

    def check_for_auto_row_add(self, item):
        row = item.row()
        last_row = self.setEditorTable.rowCount() - 1

        if row == last_row:
            word_item = self.setEditorTable.item(row, 0)
            trans_item = self.setEditorTable.item(row, 1)

            word_text = word_item.text().strip() if word_item else ""
            trans_text = trans_item.text().strip() if trans_item else ""

            if word_text or trans_text:
                self._add_editor_row("", "")
        
        self.save_table_to_file()

    def save_table_to_file(self):
        words = []
        for row in range(self.setEditorTable.rowCount()):
            word_item = self.setEditorTable.item(row, 0)
            transl_item = self.setEditorTable.item(row, 1)

            word = word_item.text().strip() if word_item else ""
            translation = transl_item.text().strip() if transl_item else ""

            if word or translation:
                words.append({
                    "word": word,
                    "translation": translation,
                    "id": len(words) + 1
                })
            
        if self.current_editing_title:
            data = Files.read(self.current_editing_title)
            data["words"] = words
            Files.record(self.current_editing_title, data)

        new_count = len(words)
        for card in self.widgets:
            if card.title_lbl.text() == self.current_editing_title:
                card.update_count(new_count)
                break


class WCard(QtWidgets.QWidget):
    def __init__(self, title: str, tag: str, word_count: int=0, parent=None):
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

        self.title_lbl = QtWidgets.QLabel(title, self)
        self.title_lbl.setWordWrap(True)
        self.title_lbl.setStyleSheet("background-color: transparent; color: white; font-size: 28px; border: none;")
        vbox.addWidget(self.title_lbl)

        self.tag_lbl = QtWidgets.QLabel(tag, self)
        self.tag_lbl.setStyleSheet("background-color: transparent; color: #797979; font-size: 14px; border: none;")
        vbox.addWidget(self.tag_lbl)

        word_counter = f"{word_count} word pair{'s' if word_count != 1 else ''}"
        self.counter_lbl = QtWidgets.QLabel(word_counter, self)
        self.counter_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.counter_lbl.setStyleSheet("background-color: transparent; color: #797979; font-size: 14px; border: none;")
        vbox.addWidget(self.counter_lbl)
        self.update_count(word_count)

    def update_count(self, n):
        self.counter_lbl.setText(f"{n} word pair{'s' if n!=1 else ''}")

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
        action_edit = menu.addAction("📝 Edit")

        action = menu.exec_(self.mapToGlobal(position))

        if action == action_delete:
            if self.owner:
                self.owner.remove_card(self)

        elif action == action_edit:
            if self.owner:
                self.owner.open_set_editor(self.title_lbl.text())

    def mouseDoubleClickEvent(self, event):
        if self.owner:
            self.owner.open_set_editor(self.title_lbl.text())
        

class Files:
    def create(name, folder=None):
        if not folder:
            folder = "cards"
        filename = f"{name}.json"
        cards_dir = os.path.join(os.getcwd(), folder)
        os.makedirs(cards_dir, exist_ok=True)
        filepath = os.path.join(cards_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)

    @staticmethod
    def last_modified(name: str, folder: str = 'cards') -> float:
        filename = name if name.lower().endswith('.json') else f"{name}.json"
        filepath = os.path.join(os.getcwd(), folder, filename)
        return os.path.getmtime(filepath)
    
    @staticmethod
    def last_modified_dt(name: str, folder: str = 'cards') -> datetime:
        ts = Files.last_modified(name, folder)
        return datetime.fromtimestamp(ts)

    @staticmethod
    def delete(name, folder="cards"):
        filename = f"{name}.json"
        cards_dir = os.path.join(os.getcwd(), folder)
        filepath = os.path.join(cards_dir, filename)

        if os.path.exists(filepath):
            os.remove(filepath)
        else:
            print(f"Could not delete {filepath!r}: file isn't found.")

    def exists(name: str, folder: str = "cards"):
        filename = name if name.lower().endswith(".json") else f"{name}.json"
        cards_dir = os.path.join(os.getcwd(), folder)
        filepath = os.path.join(cards_dir, filename)
        return os.path.isfile(filepath)


    def read(name: str, folder: str = "cards") -> dict:
        
        filename = name if name.lower().endswith(".json") else f"{name}.json"
        cards_dir = os.path.join(os.getcwd(), folder)
        filepath = os.path.join(cards_dir, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Could not find file: {filepath!r}")

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
        

    def record(name, data, folder="cards"):
        filename = f"{name}.json"
        cards_dir = os.path.join(os.getcwd(), folder)
        filepath = os.path.join(cards_dir, filename)

        if os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as file:
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
