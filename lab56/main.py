from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QMainWindow, QCompleter, QFileDialog
import sys
from source.view import Ui_MainWindow
from source.model import Document, Model
from os import path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        self.model = Model("source/data/docs.sqlite3")
        self.cur_docs = []
        self.words_to_highlight = []
        self.setup_completer()
        self.ui.link_label.setText('Ссылка на документ')
        self.ui.link_label.setOpenExternalLinks(True)
        self.connect_signals()

        self.update()

    def connect_signals(self):
        self.ui.add_pushButton.clicked.connect(self.add_doc_button_handler)
        self.ui.docs_listWidget.currentRowChanged.connect(self.docs_list_item_changed_handler)
        self.ui.search_pushButton.clicked.connect(self.search_button_clicked_handler)
        self.ui.del_pushButton.clicked.connect(self.del_doc_button_handler)
        self.ui.link_label.linkActivated.connect(self.open_file_explorer)

    def add_doc_button_handler(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Все файлы (*.*)")
        if file_path:
            with open(file_path, "rt") as f:
                content = f.read()
                # print(f.name[:-4], content, datetime.now().strftime("%Y-%m-%d"))
                self.model.add_doc(name=path.basename(file_path), content=content, path=file_path)
        self.update()

    def search_button_clicked_handler(self):
        self.cur_docs, self.words_to_highlight = self.model.search_docs(self.ui.search_lineEdit.text())
        self.update()

    def del_doc_button_handler(self):
        if self.ui.docs_listWidget.currentRow() >= 0:
            self.model.del_doc(self.cur_docs[self.ui.docs_listWidget.currentRow()].doc_id)
            self.update()

    def update(self):
        self.cur_docs = self.model.get_all_docs()
        self.update_list()
        self.ui.doc_textEdit.clear()

    def update_list(self):
        self.ui.docs_listWidget.clear()
        for doc in self.cur_docs:
            self.ui.docs_listWidget.addItem(doc.name)

    def docs_list_item_changed_handler(self, index):
        if index != -1:
            content = self.cur_docs[index].content
            self.ui.doc_textEdit.setText(content)
            self.ui.link_label.setText(
                f'<a href="{path.dirname(self.cur_docs[index].path)}">Ссылка на документ</a>')
        else:
            self.ui.link_label.setText(f'Ссылка на документ')
            self.ui.doc_textEdit.clear()

    def setup_completer(self):
        completer_list = self.model.get_completer_list()
        completer = QCompleter(completer_list, self.ui.search_lineEdit)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.ui.search_lineEdit.setCompleter(completer)

    def open_file_explorer(self, filepath):
        QDesktopServices.openUrl(filepath)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    app.exec()