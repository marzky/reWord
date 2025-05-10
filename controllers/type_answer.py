import random
from difflib import SequenceMatcher
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer
from core.files import Files


class TypeAnswer():
    def __init__(self, parent):
        self.parent = parent
        self.layout = parent.findChild(QtWidgets.QVBoxLayout, "typeAnswerLayout")
        self.title = None
        self.words = []
        self.index = 0
        self.checked = False

    def start(self, title):
        self.title = title
        data = Files.read(title)
        self.words = data.get("words", []).copy()
        if not self.words:
            return
        random.shuffle(self.words)
        self.index = 0
        self.checked = False
        self.parent.pages.setCurrentWidget(self.parent.typeAnswerView)
        self.show()

    def show(self):
        layout = self.layout
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget() or item.layout()
            if w:
                w.setParent(None)

        if self.index >= len(self.words):
            random.shuffle(self.words)
            self.index = 0

        word = self.words[self.index]["word"]
        correct = self.words[self.index]["translation"]

        count_lbl = QtWidgets.QLabel(f"{self.index + 1} / {len(self.words)}", alignment=Qt.AlignHCenter | Qt.AlignTop)
        count_lbl.setStyleSheet("font: 20px 'Funnel Sans Light'; color: white;")
        layout.addWidget(count_lbl)

        layout.addStretch()

        word_lbl = QtWidgets.QLabel(word, alignment=Qt.AlignCenter)
        word_lbl.setStyleSheet("font-size: 24px; color: white;")
        layout.addWidget(word_lbl)

        layout.addStretch()

        self.result_lbl = QtWidgets.QLabel("", alignment=Qt.AlignCenter)
        self.result_lbl.setStyleSheet("font-size: 18px; color: #888;")
        layout.addWidget(self.result_lbl)

        self.answer_input = QtWidgets.QLineEdit()
        self.answer_input.setPlaceholderText("Enter translation")
        self.answer_input.setStyleSheet("font: 20px 'Funnel Sans Light'; color: white; background-color: #1B1B1B; padding: 8px; border-radius: 7px;")
        self.answer_input.setEnabled(True)
        QTimer.singleShot(0, self.answer_input.setFocus)
        layout.addWidget(self.answer_input)

        self.check_btn = QtWidgets.QPushButton("Check")
        self.check_btn.setStyleSheet("""QPushButton{
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
        self.check_btn.setFixedHeight(40)
        self.check_btn.clicked.connect(self.check)
        layout.addWidget(self.check_btn)

    def check(self):
        if self.checked:
            return

        user_input = self.answer_input.text().strip().lower()
        correct = self.words[self.index]["translation"].strip().lower()

        ratio = SequenceMatcher(None, user_input, correct).ratio()
        percent = round(ratio * 100)

        if percent == 100:
            self.result_lbl.setText("Correct!")
            self.result_lbl.setStyleSheet("font: 20px 'Funnel Sans Light'; color: white;")
        else:
            self.result_lbl.setText(f"{percent}% match\nCorrect: {correct}")
            self.result_lbl.setStyleSheet("font: 20px 'Funnel Sans Light'; color: #FF2C55;")

        self.check_btn.setText("Next card")
        self.check_btn.clicked.disconnect()
        self.check_btn.clicked.connect(self.next)

        self.answer_input.setDisabled(True)
        self.checked = True

    def next(self):
        self.index += 1
        self.checked = False
        self.show()