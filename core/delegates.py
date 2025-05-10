from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStyledItemDelegate, QStyle


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