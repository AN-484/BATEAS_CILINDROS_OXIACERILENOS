from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

class TableView(QTableWidget):
    def cargar_datos(self, headers, data):
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setRowCount(len(data))

        for row_idx, row in enumerate(data):
            for col_idx, value in enumerate(row):
                self.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))