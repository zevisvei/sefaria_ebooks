import sys
import traceback
import os

from sefaria import sefaria_api, utils, get_from_sefaria

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QScrollArea,
    QLineEdit,
    QCompleter,
    QHeaderView
)
from PyQt6.QtCore import Qt


class CommentarySelectionDialog(QDialog):
    def __init__(self, commentaries, parent=None):
        super().__init__(parent)
        self.setWindowTitle("בחירת פרשנויות")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(400, 500)

        self.commentaries = commentaries
        self.checkboxes = []

        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_contents = QWidget()
        scroll_layout = QVBoxLayout(scroll_contents)
        scroll_layout.setContentsMargins(5, 5, 5, 5)

        for commentary in commentaries:
            checkbox = QCheckBox(commentary)
            scroll_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        scroll_contents.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_contents)
        main_layout.addWidget(scroll_area)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def get_selected(self):
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]


def run_script(book: dict, lang: str, get_links: bool = False):
    try:
        print("Running for book:", book)
        file_name = utils.sanitize_filename(book['he_title'] if lang == "hebrew" else book['en_title'])
        html_file = f"{file_name}.html"
        epub_file = f"{file_name}.epub"

        result = get_from_sefaria.Book(
            book["en_title"], lang, book["he_title"], book["path"], get_links=get_links
        )
        if not result.exists:
            print("Book does not exist")
            return

        book_dir = ' dir="rtl"' if lang == "hebrew" else ""
        book_content = result.process_book()

        if get_links:
            commentary_list = list(result.all_commentaries)
            if commentary_list:
                dialog = CommentarySelectionDialog(commentary_list)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected = dialog.get_selected()
                    if selected:
                        result.add_links(selected)
                        book_content = result.book_content

        if not book_content:
            return

        book_content = f'<html lang="{lang[:2]}"><head><meta charset="utf-8"><title></title></head><body{book_dir}>{"".join(book_content)}</body></html>'
        if "footnote-marker" in book_content:
            book_content = utils.footnotes_to_epub(book_content)
        metadata = result.get_metadata()

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(book_content)
        if metadata is None:
            metadata = {}

        utils.to_ebook(html_file, epub_file, metadata)
        print(f"Created {epub_file}")
        os.remove(html_file)

    except Exception:
        print(traceback.format_exc())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ספרי ספריא")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        settings_layout = QHBoxLayout()

        lang_label = QLabel("בחר שפה:")
        settings_layout.addWidget(lang_label)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["עברית", "אנגלית"])
        settings_layout.addWidget(self.language_combo)

        self.links_checkbox = QCheckBox("הוסף קישורים לפרשנויות")
        settings_layout.addWidget(self.links_checkbox)

        self.search_line = QLineEdit()
        self.search_line.setPlaceholderText("חפש ספר...")
        settings_layout.addWidget(self.search_line)

        settings_layout.addStretch()
        main_layout.addLayout(settings_layout)

        self.table = QTableWidget()
        main_layout.addWidget(self.table)

        self.books_list = []
        self.load_books()

        all_titles = []
        for book in self.books_list:
            en_title = book.get("en_title", "")
            he_title = book.get("he_title", "")
            if en_title:
                all_titles.append(en_title)
            if he_title:
                all_titles.append(he_title)

        completer = QCompleter(all_titles, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_line.setCompleter(completer)

        self.search_line.textChanged.connect(self.filter_table)

    def load_books(self):
        try:
            sefaria_api_instance = sefaria_api.SefariaApi()
            all_books = sefaria_api_instance.table_of_contents()
            self.books_list = utils.recursive_register_categories(all_books)

            self.table.setRowCount(len(self.books_list))
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["כותרת (אנגלית)", "כותרת (עברית)", "הרץ"])

            for row, book in enumerate(self.books_list):
                en_title = book.get("en_title", "N/A")
                he_title = book.get("he_title", "N/A")

                self.table.setItem(row, 0, QTableWidgetItem(en_title))
                self.table.setItem(row, 1, QTableWidgetItem(he_title))

                btn = QPushButton("הרץ")
                btn.clicked.connect(lambda checked, b=book: self.run_script_for_book(b))
                self.table.setCellWidget(row, 2, btn)

            # הסתרת כותרת השורות
            self.table.verticalHeader().setVisible(False)

            header = self.table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", str(e))

    def run_script_for_book(self, book):
        try:
            lang_mapping = {"עברית": "hebrew", "אנגלית": "english"}
            lang_choice = self.language_combo.currentText()
            lang = lang_mapping.get(lang_choice, "hebrew")
            get_links = self.links_checkbox.isChecked()

            run_script(book, lang, get_links=get_links)
            QMessageBox.information(
                self,
                "בוצע",
                f"הסקריפט רץ עבור: {book.get('he_title', 'N/A')}",
            )
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", str(e))

    def filter_table(self):
        text = self.search_line.text().strip().lower()
        for row in range(self.table.rowCount()):
            en_item = self.table.item(row, 0)
            he_item = self.table.item(row, 1)

            row_visible = False
            if en_item and text in en_item.text().lower():
                row_visible = True
            if he_item and text in he_item.text().lower():
                row_visible = True

            self.table.setRowHidden(row, not row_visible)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
