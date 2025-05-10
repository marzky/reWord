from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QRegExp, QTimer
from PyQt5.QtGui import QRegExpValidator, QKeySequence
from core.core_utils import Core
from controllers.layout_and_filters import LayoutFilter
from core.files import Files
from controllers.flashcards import Flashcards
from controllers.type_answer import TypeAnswer
from controllers.sets import Sets


class reWord(QtWidgets.QMainWindow, Sets, LayoutFilter):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/reWord.ui", self)
        self.setWindowTitle("reWord")
        hwnd = int(self.winId())
        Core.set_title_bar_color(hwnd)

        # Cards parameters
        self.widget_width = 185
        self.widget_height = 185
        self.widgets = []

        # Initial set loading from Cards directory
        self.load_all_sets()

        self.filtering_mode = 'Date' # 'date', 'title', 'tag', 'group'
        self.sort_order = 'asc' # 'asc', 'desc'

        regexp = QRegExp(r"[A-Za-zА-Яа-я0-9 _-]+")
        validator = QRegExpValidator(regexp)

        new_set_shortcut = QtWidgets.QShortcut(QKeySequence("Ctrl+N"), self)
        new_set_shortcut.activated.connect(lambda: self.new_set(self))

        self.pages.setCurrentWidget(self.mainPage)
        self.newSetBtn.clicked.connect(lambda: (Sets.new_set(self), self.relayout_widgets()))
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

        self.editSetBtn.clicked.connect(lambda: self.open_set_editor(self.current_editing_title))

        
        self.flashcards = Flashcards(self)
        self.flashcardsBtn.clicked.connect(lambda: self.flashcards.start(self.current_editing_title))
        self.flashcardsLayout = self.findChild(QtWidgets.QVBoxLayout, "flashcardsLayout")

        self.typeAnswer = TypeAnswer(self)
        self.typeAnswerBtn.clicked.connect(lambda: self.typeAnswer.start(self.current_editing_title))

        QTimer.singleShot(0, self.filtering_widgets)

    def open_wt_menu(self, title: str):
        self.current_editing_title = title
        self.pages.setCurrentWidget(self.modeChoosingPage)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.relayout_widgets()

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

    def keyPressEvent(self, event):
        if self.pages.currentWidget() == self.flashcardsView:
            if event.key() == Qt.Key_Space:
                self.flashcards.flip()
            elif event.key() == Qt.Key_Right:
                self.flashcards.next()
            elif event.key() == Qt.Key_Left:
                self.flashcards.prev()
            elif event.key() == Qt.Key_Escape:
                self.pages.setCurrentWidget(self.mainPage)
            event.accept()

        elif self.pages.currentWidget() == self.typeAnswerView:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if self.typeAnswer.checked:
                    self.typeAnswer.next()
                else:
                    self.typeAnswer.check()
                event.accept()
            elif event.key() == Qt.Key_Escape:
                self.pages.setCurrentWidget(self.mainPage)
                event.accept()
            else:
                super().keyPressEvent(event)

        else:
            if event.key() == Qt.Key_Escape:
                self.pages.setCurrentWidget(self.mainPage)
            else:
                super().keyPressEvent(event)