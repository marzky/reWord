import json, os, glob
from PyQt5 import QtWidgets
from core.core_utils import Core
from core.delegates import CleanNavigationDelegate
from core.files import Files
from app.wcard import WCard


class Sets():
    # New set page opener
    def new_set(self):
        self.newSetEdit.clear()
        self.tagEdit.clear()
        self.pages.setCurrentWidget(self.newSetPage)
        self.newSetEdit.setFocus()

    # New set creation process 
    def create_set(self):
        set_name = self.newSetEdit.text()
        if not set_name:
            Core.create_warning_box("Could not create a set", "Title shouldn't be empty.")
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
            Core.create_warning_box("Could not create a set", "Set title is already in Cards directory. Please, change the title.")
            return
    
    # Set editor opener
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

        self.setEditorTable.scrollToBottom()
        self.setEditorTable.blockSignals(False)


        last_row = self.setEditorTable.rowCount() - 1
        if last_row >= 0:
            self.setEditorTable.setCurrentCell(last_row, 0)
            self.setEditorTable.editItem(self.setEditorTable.item(last_row, 0))

    # Loading sets from cards directory
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

    def paste_from_clipboard(self):
        self.setEditorTable.closePersistentEditor(self.setEditorTable.currentItem())
        self.setEditorTable.clearFocus() 
        cb = QtWidgets.QApplication.clipboard()
        text = cb.text()
        if not text:
            return

        lines = [r for r in text.strip().splitlines() if r]
        start_row = self.setEditorTable.currentRow()
        start_col = self.setEditorTable.currentColumn()
        if start_row < 0: start_row = self.setEditorTable.rowCount()

        for i, line in enumerate(lines):
            cols = line.split('\t')
            r = start_row + i
            
            if r >= self.setEditorTable.rowCount():
                self.setEditorTable.insertRow(r)
            for j, cell in enumerate(cols[:2]): 
                c = start_col + j
                item = QtWidgets.QTableWidgetItem(cell.strip().strip('"'))
                self.setEditorTable.setItem(r, c, item)

        self.save_table_to_file()

        last_row = start_row + len(lines) - 1
        if last_row >= self.setEditorTable.rowCount():
            last_row = self.setEditorTable.rowCount() - 1
        self.setEditorTable.setCurrentCell(last_row, 0)
        self.setEditorTable.setFocus()