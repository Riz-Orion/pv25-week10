import sqlite3
import csv
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class BookManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Buku")
        self.setGeometry(100, 100, 700, 500)
        self.conn = sqlite3.connect("books.db")
        self.c = self.conn.cursor()
        self.c.execute("""CREATE TABLE IF NOT EXISTS books (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          title TEXT, author TEXT, year INTEGER)""")
        self.conn.commit()
        self.initUI()

    def initUI(self):
        self.createMenuBar()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dataTab = QWidget()
        self.exportTab = QWidget()
        self.tabs.addTab(self.dataTab, "Data Buku")
        self.tabs.addTab(self.exportTab, "Ekspor")

        self.initDataTab()
        self.initExportTab()

    def createMenuBar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        save_action = QAction("Simpan", self)
        save_action.triggered.connect(self.saveData)
        export_action = QAction("Ekspor CSV", self)
        export_action.triggered.connect(self.exportCSV)
        exit_action = QAction("Keluar", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(save_action)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("Edit")
        search_action = QAction("Cari Judul", self)
        search_action.triggered.connect(lambda: self.searchInput.setFocus())
        delete_action = QAction("Hapus Data", self)
        delete_action.triggered.connect(self.deleteData)
        edit_menu.addAction(search_action)
        edit_menu.addAction(delete_action)

    def initDataTab(self):
        layout = QVBoxLayout()

        self.infoLabel = QLabel("Nama: Rizky Maulana Ramdhani | NIM: F1D022095")
        layout.addWidget(self.infoLabel)

        form_layout = QHBoxLayout()
        self.titleInput = QLineEdit()
        self.authorInput = QLineEdit()
        self.yearInput = QLineEdit()
        self.saveBtn = QPushButton("Simpan")
        self.saveBtn.clicked.connect(self.saveData)

        form_layout.addWidget(QLabel("Judul:"))
        form_layout.addWidget(self.titleInput)
        form_layout.addWidget(QLabel("Pengarang:"))
        form_layout.addWidget(self.authorInput)
        form_layout.addWidget(QLabel("Tahun:"))
        form_layout.addWidget(self.yearInput)
        form_layout.addWidget(self.saveBtn)
        layout.addLayout(form_layout)

        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("Cari judul...")
        self.searchInput.textChanged.connect(self.searchData)
        layout.addWidget(self.searchInput)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.table.cellDoubleClicked.connect(self.editCell)
        layout.addWidget(self.table)

        self.deleteBtn = QPushButton("Hapus Data")
        self.deleteBtn.clicked.connect(self.deleteData)
        layout.addWidget(self.deleteBtn)

        self.dataTab.setLayout(layout)
        self.loadData()

    def initExportTab(self):
        layout = QVBoxLayout()
        label = QLabel("Klik tombol di bawah ini untuk mengekspor data ke CSV.")
        label.setAlignment(Qt.AlignCenter)
        self.exportBtn = QPushButton("Ekspor ke CSV")
        self.exportBtn.clicked.connect(self.exportCSV)

        layout.addWidget(label)
        layout.addWidget(self.exportBtn)
        self.exportTab.setLayout(layout)

    def saveData(self):
        title = self.titleInput.text()
        author = self.authorInput.text()
        year = self.yearInput.text()
        if title and author and year:
            self.c.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
                           (title, author, year))
            self.conn.commit()
            self.titleInput.clear()
            self.authorInput.clear()
            self.yearInput.clear()
            self.loadData()
        else:
            QMessageBox.warning(self, "Error", "Semua kolom harus diisi!")

    def loadData(self):
        self.table.setRowCount(0)
        self.c.execute("SELECT * FROM books")
        for row_data in self.c.fetchall():
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def searchData(self):
        keyword = self.searchInput.text().lower()
        self.table.setRowCount(0)
        self.c.execute("SELECT * FROM books WHERE LOWER(title) LIKE ?", ('%' + keyword + '%',))
        for row_data in self.c.fetchall():
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def deleteData(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data yang dipilih!")
            return

        book_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self,
            "Konfirmasi",
            f"Yakin ingin menghapus buku dengan ID {book_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.c.execute("DELETE FROM books WHERE id = ?", (book_id,))
            self.conn.commit()
            self.loadData()

    def editCell(self, row, column):
        old_value = self.table.item(row, column).text()
        new_value, ok = QInputDialog.getText(self, "Edit Data", "Ubah nilai:", text=old_value)
        if ok and new_value:
            book_id = self.table.item(row, 0).text()
            column_name = ["id", "title", "author", "year"][column]
            self.c.execute(f"UPDATE books SET {column_name} = ? WHERE id = ?", (new_value, book_id))
            self.conn.commit()
            self.loadData()

    def exportCSV(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan file", "", "CSV Files (*.csv)")
        if path:
            with open(path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                self.c.execute("SELECT * FROM books")
                for row in self.c.fetchall():
                    writer.writerow(row)
            QMessageBox.information(self, "Sukses", "Data berhasil diekspor ke CSV.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookManager()
    window.show()
    sys.exit(app.exec_())

