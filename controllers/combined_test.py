from core.files import Files
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import random


class CombinedTest:
    def __init__(self, parent):
        self.parent = parent
        self.layout = parent.findChild(QtWidgets.QVBoxLayout, "combinedTestLayout")
        self.tag_checkboxes = []
        self.shuffle_checkbox = None
        self.select_all_checkbox = None
        self.setup_menu()
        self.updating_tags = False

    def get_all_tags(self):
        tags = set()
        for title in Files.get_all_titles():
            data = Files.read(title)
            tag = data.get("tag")
            if tag:
                tags.add(tag)
        return sorted(tags)

    def setup_menu(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        all_tags = self.get_all_tags()

        self.layout.addStretch()

        self.lbl = QtWidgets.QLabel("Choose tags")
        self.lbl.setStyleSheet("font-size: 24px; color: white;")
        self.layout.addWidget(self.lbl)

        self.select_all_checkbox = QtWidgets.QCheckBox("Select all tags")
        self.select_all_checkbox.setStyleSheet("color: white; font: 20px 'Funnel Sans Light';")
        self.select_all_checkbox.stateChanged.connect(self.toggle_all_tags)
        self.layout.addWidget(self.select_all_checkbox)

        self.shuffle_checkbox = QtWidgets.QCheckBox("Shuffle questions")
        self.shuffle_checkbox.setStyleSheet("color: white; font: 20px 'Funnel Sans Light';")
        self.layout.addWidget(self.shuffle_checkbox)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setStyleSheet("color: #555; background-color: #555; max-height: 1px;")
        self.layout.addWidget(line)

        self.tag_checkboxes = []
        for tag in all_tags:
            cb = QtWidgets.QCheckBox(tag)
            cb.stateChanged.connect(self.on_tag_changed)
            cb.setStyleSheet("color: white; font: 20px 'Funnel Sans Light';")
            self.layout.addWidget(cb)
            self.tag_checkboxes.append(cb)

        self.layout.addStretch()

        start_btn = QtWidgets.QPushButton("Start combined test")
        start_btn.setStyleSheet("""QPushButton{
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
        start_btn.clicked.connect(self.start_combined_test)
        start_btn.setFixedHeight(40)
        self.layout.addWidget(start_btn)

    def toggle_all_tags(self, state):
        self.updating_tags = True
        checked = state == QtCore.Qt.Checked
        for cb in self.tag_checkboxes:
            cb.setChecked(checked)
        self.updating_tags = False

    def on_tag_changed(self):
        if self.updating_tags:
            return 

        all_checked = all(cb.isChecked() for cb in self.tag_checkboxes)
        self.select_all_checkbox.blockSignals(True)
        self.select_all_checkbox.setChecked(all_checked)
        self.select_all_checkbox.blockSignals(False)

    def start_combined_test(self):
        selected_tags = [cb.text() for cb in self.tag_checkboxes if cb.isChecked()]
        shuffle = self.shuffle_checkbox.isChecked()
        if not selected_tags:
            QtWidgets.QMessageBox.warning(self.parent, "No tags", "Select at least one tag.")
            return

        # собрать все слова по выбранным тегам
        words = []
        for title in Files.get_all_titles():
            data = Files.read(title)
            if data.get("tag") in selected_tags:
                words.extend(data.get("words", []))

        if shuffle:
            random.shuffle(words)

        # запустить тест — тут можно передать в test.start_combined(...)
        self.parent.start_combined_test(words)