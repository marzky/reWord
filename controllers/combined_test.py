from core.files import Files
from PyQt5 import QtWidgets, QtCore
import random


class CombinedTest:
    def __init__(self, parent):
        self.parent = parent
        self.container_layout = parent.findChild(QtWidgets.QVBoxLayout, "combinedTestContainerLayout")

        # ScrollArea и содержимое
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
                                    QScrollBar:vertical {
                                        background: transparent;
                                        width: 12px;
                                        margin: 0px;
                                    }

                                    QScrollBar::handle:vertical {
                                        background: #050505;
                                        min-height: 30px;
                                        border-radius: 6px; 
                                        border: 1.5px solid #1B1B1B;
                                    }

                                    QScrollBar::sub-line:vertical,
                                    QScrollBar::add-line:vertical {
                                        height: 0px;
                                        subcontrol-origin: margin;
                                        subcontrol-position: top; 
                                        background: none;
                                    }

                                    QScrollBar::sub-page:vertical,
                                    QScrollBar::add-page:vertical {
                                        background: none;
                                    }

                                    QScrollBar:horizontal { height:12px; }
                                    QScrollBar::handle:horizontal {
                                        background:#555; border-radius:6px; min-width:30px;
                                    }
                                    """)

        self.scroll_content = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        self.scroll_area.setWidget(self.scroll_content)
        self.container_layout.addWidget(self.scroll_area)

        self.tag_buttons = []
        self.shuffle_button = None
        self.select_all_button = None
        self.updating_tags = False

    def refresh(self):
        self.setup_menu()

    def get_all_tags(self):
        tags = set()
        for title in Files.get_all_titles():
            data = Files.read(title)
            tag = data.get("tag")
            if tag:
                tags.add(tag)
        return sorted(tags)

    def create_toggle_button(self, text):
        btn = QtWidgets.QPushButton(text)
        btn.setCheckable(True)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #1B1B1B;
                border-radius: 12px;
                color: white;
                font: 18px 'Funnel Sans';
                padding: 10px 16px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2D2D2D;
            }
            QPushButton:checked {
                background-color: #C41E3D;
            }
        """)
        return btn

    def setup_menu(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        all_tags = self.get_all_tags()

        lbl = QtWidgets.QLabel("Choose tags")
        lbl.setStyleSheet("font-size: 24px; color: white;")
        self.layout.addWidget(lbl)

        # Select all tags button
        self.select_all_button = self.create_toggle_button("Select all tags")
        self.select_all_button.toggled.connect(self.toggle_all_tags)
        self.layout.addWidget(self.select_all_button)

        # Shuffle button
        self.shuffle_button = self.create_toggle_button("Shuffle questions")
        self.layout.addWidget(self.shuffle_button)

        # Divider
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setStyleSheet("color: #555; background-color: #555; max-height: 1px;")
        self.layout.addWidget(line)

        # Tag buttons
        self.tag_buttons = []
        for tag in all_tags:
            btn = self.create_toggle_button(tag)
            btn.toggled.connect(self.on_tag_changed)
            self.layout.addWidget(btn)
            self.tag_buttons.append(btn)

        self.layout.addStretch()

        # Start button
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

    def toggle_all_tags(self, checked):
        self.updating_tags = True
        for btn in self.tag_buttons:
            btn.setChecked(checked)
        self.updating_tags = False

    def on_tag_changed(self):
        if self.updating_tags:
            return

        all_checked = all(btn.isChecked() for btn in self.tag_buttons)
        self.select_all_button.blockSignals(True)
        self.select_all_button.setChecked(all_checked)
        self.select_all_button.blockSignals(False)

    def start_combined_test(self):
        selected_tags = [btn.text() for btn in self.tag_buttons if btn.isChecked()]
        shuffle = self.shuffle_button.isChecked()
        if not selected_tags:
            QtWidgets.QMessageBox.warning(self.parent, "No tags", "Select at least one tag.")
            return

        words = []
        for title in Files.get_all_titles():
            data = Files.read(title)
            if data.get("tag") in selected_tags:
                words.extend(data.get("words", []))

        if shuffle:
            random.shuffle(words)

        self.parent.start_combined_test(words)