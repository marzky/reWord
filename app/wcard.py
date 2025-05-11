from PyQt5 import QtWidgets, QtCore


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
            self.owner.open_wt_menu(self.title_lbl.text())