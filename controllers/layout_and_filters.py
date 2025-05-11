from core.files import Files
from PyQt5.QtCore import Qt


class LayoutFilter():

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

    def on_filter_changed(self, index: int):
        if 0 <= index < len(self.filter_modes):
            self.filtering_mode = self.filter_modes[index]
        self.filtering_widgets()

    def on_sort_order_changed(self, order):
        self.sort_order = order
        self.filtering_widgets()