import random
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer
from core.files import Files


class Flashcards():
    def __init__(self, parent):
        self.parent = parent
        self.flashcardsLayout = parent.findChild(QtWidgets.QVBoxLayout, "flashcardsLayout")
        self.current_editing_title = None
        self.words = []
        self.index = 0
        self.shown = False

    def clear_layout(self, layout=None):
        if layout is None:
            layout = self.flashcardsLayout

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()

            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            elif child_layout is not None:
                self.clear_layout(child_layout)
                child_layout.setParent(None)

    def start(self, title):
        self.current_editing_title = title
        data = Files.read(title)
        self.words = data.get("words", []).copy()
        if not self.words:
            return
        random.shuffle(self.words)
        self.index = 0
        self.shown = False
        self.parent.pages.setCurrentWidget(self.parent.flashcardsView)
        self.show()

    def show(self):
        layout = self.flashcardsLayout
        self.clear_layout()

        if not self.words:
            return

        word = self.words[self.index]["word"]
        translation = self.words[self.index]["translation"]
        text = translation if self.shown else word

        count_lbl = QtWidgets.QLabel(f"{self.index + 1} / {len(self.words)}", alignment=Qt.AlignHCenter | Qt.AlignTop)
        count_lbl.setStyleSheet("font: 20px 'Funnel Sans Light'; color: white;")
        layout.addWidget(count_lbl)

        layout.addStretch()

        word_lbl = QtWidgets.QLabel(text, alignment=Qt.AlignCenter)
        word_lbl.setStyleSheet("font-size: 24px; color: white;")
        word_lbl.setWordWrap(True)
        layout.addWidget(word_lbl)

        layout.addStretch()

        btn_show = QtWidgets.QPushButton("Hide answer" if self.shown else "Show answer")
        btn_show.clicked.connect(self.flip)
        btn_show.setFixedHeight(40)
        btn_show.setStyleSheet("""QPushButton{
                    background-color: #1B1B1B;
                    border-radius: 7px;
                    color: white;
                    font: 20px "Funnel Sans";
                    }

                    QPushButton::hover{
                    background-color: #2D2D2D;
                    }

                    QPushButton::pressed{
                    background-color: #1B1B1B;
                    }""")
        layout.addWidget(btn_show)

        nav = QtWidgets.QHBoxLayout()
        btn_prev = QtWidgets.QPushButton("Previous word")
        btn_next = QtWidgets.QPushButton("Next word")
        for btn, action in [(btn_prev, self.prev), (btn_next, self.next)]:
            btn.setFixedHeight(40)
            btn.setStyleSheet("""QPushButton{
                    background-color: #1B1B1B;
                    border-radius: 7px;
                    color: white;
                    font: 20px "Funnel Sans";
                    }

                    QPushButton::hover{
                    background-color: #2D2D2D;
                    }

                    QPushButton::pressed{
                    background-color: #1B1B1B;
                    }""")
            btn.clicked.connect(action)
            nav.addWidget(btn)
        layout.addLayout(nav)

        QTimer.singleShot(0, self.parent.setFocus)

    def flip(self):
        self.shown = not self.shown
        self.show()

    def next(self):
        if self.index + 1 < len(self.words):
            self.index += 1
            self.shown = False
            self.show()

    def prev(self):
        if self.index > 0:
            self.index -= 1
            self.shown = False
            self.show()
