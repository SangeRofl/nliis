import view
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt6.QtGui import QDesktopServices
import sqlite3
from datetime import datetime
import sys
from os import path
from bs4 import BeautifulSoup
from lang_recog_model import LangRecognModel, Lang
from n_gram_model import NGramModel
from alpha_model import AlphaModel
from neural_model import NeuralModel
from enum import Enum
import matplotlib.pyplot as plt


class LangRecognMethod(Enum):
    n_gram = "N-грамм"
    alpha = "алфавитный"
    neural = "нейросетевой"


class Document:
    def __init__(self, name, content, date, doc_id, path):
        self.name = name
        self.content = content
        self.date = date
        self.doc_id = doc_id
        self.path = path



class Model:
    def __init__(self, db_name: str = 'docs.db'):
        self.db_docs_conn = sqlite3.connect(db_name)
        self.db_docs_cur = self.db_docs_conn.cursor()
        self.connect_to_doc_database()
        self.n_gram_model = NGramModel()
        self.alpha_model = AlphaModel()
        self.neural_model = NeuralModel()
        self.statistics_data = {i: [] for i in Lang.__members__.values()}

    def connect_to_doc_database(self):
        self.db_docs_cur.execute("""
        CREATE TABLE IF NOT EXISTS docs(
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           name TEXT,
           content TEXT,
           date TEXT,
           path TEXT);
        """)
        self.db_docs_conn.commit()
        self.db_docs_cur.execute("SELECT * FROM docs;")

    def get_docs(self, indexes):
        res = []
        ph = ', '.join(['?' for _ in indexes])
        self.db_docs_cur.execute(f"SELECT * FROM docs WHERE id IN ({ph});", indexes)
        for i in self.db_docs_cur.fetchall():
            res.append(self.get_doc_from_data(i))
        return res

    @staticmethod
    def get_raw_text_from_html(html_text) -> str:
        return BeautifulSoup(html_text, "html.parser").get_text()

    def get_all_docs(self):
        ids = []
        self.db_docs_cur.execute(f"SELECT id FROM docs;")
        for i in self.db_docs_cur.fetchall():
            ids.append(i[0])
        return self.get_docs(ids)

    @staticmethod
    def get_doc_from_data(data) -> Document:
        return Document(doc_id=data[0], name=data[1], content=data[2], date=data[3], path=data[4])

    def add_doc(self, name, content, path):
        date = datetime.now().strftime("%Y-%m-%d")
        self.db_docs_cur.execute(f"""
                                    INSERT INTO docs(name, content, date, path)
                                    VALUES(?, ?, ?, ?);
                                    """, (name, content, date, path))
        self.db_docs_conn.commit()

    def del_doc(self, index):
        self.db_docs_cur.execute(f"DELETE FROM docs WHERE id = {index};")
        self.db_docs_conn.commit()

    def recognize_text_lang(self, html_text: str, method_name: LangRecognMethod):
        text = self.get_raw_text_from_html(html_text)
        res = None
        if method_name == LangRecognMethod.n_gram:
            res = self.n_gram_model.recognize_language(text)
        elif method_name == LangRecognMethod.alpha:
            res = self.alpha_model.recognize_language(text)
        elif method_name == LangRecognMethod.neural:
            res = self.neural_model.recognize_language(text)
        return res

    def create_statistics(self, method: LangRecognMethod):
        docs = self.get_all_docs()
        self.statistics_data.clear()
        for doc in docs:
            lang = self.recognize_text_lang(doc.content, method)
            if lang in self.statistics_data.keys():
                self.statistics_data[lang].append(doc)
            else:
                self.statistics_data[lang] = [doc]
        self.conf_statistics_plot()

    def show_statistics(self):
        self.conf_statistics_plot()
        plt.show()

    def conf_statistics_plot(self):
        vals = []
        lbls = []
        for lang, docs in self.statistics_data.items():
            vals.append(len(docs))
            lbls.append(lang.value)
        plt.pie(vals, labels=lbls, autopct='%1.1f%%')
        plt.title("Распределение языков текстов")

    def save_statistics_file(self, file_path):
        self.conf_statistics_plot()
        plt.savefig(file_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = view.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        self.connect_signals()

        self.model = Model()
        self.cur_docs = []
        self.ui.doc_link_label.setOpenExternalLinks(True)
        self.update()

    def connect_signals(self):
        self.ui.add_doc_pushButton.clicked.connect(self.add_doc_button_handler)
        self.ui.docs_listWidget.currentRowChanged.connect(self.docs_list_item_changed_handler)
        self.ui.doc_link_label.linkActivated.connect(self.link_activated_handler)
        self.ui.delete_pushButton.clicked.connect(self.delete_doc_button_handler)
        self.ui.analyze_pushButton.clicked.connect(self.analyze_button_handler)
        self.ui.view_pushButton.clicked.connect(self.view_button_handler)
        self.ui.save_pushButton.clicked.connect(self.save_button_handler)

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
            self.ui.doc_link_label.setText(f'<a href="{path.dirname(self.cur_docs[index].path)}">Ссылка на документ</a>')
            self.model.get_raw_text_from_html(self.cur_docs[index].content)
        else:
            self.ui.doc_link_label.setText(f'Ссылка на документ')
            self.ui.doc_textEdit.clear()

    def delete_doc_button_handler(self):
        if self.ui.docs_listWidget.currentRow() >= 0:
            self.model.del_doc(self.cur_docs[self.ui.docs_listWidget.currentRow()].doc_id)
            self.update()

    def add_doc_button_handler(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Все файлы (*.*)")
        if file_path:
            with open(file_path, "rt", encoding="utf-8") as f:
                content = f.read()
                # print(f.name[:-4], content, datetime.now().strftime("%Y-%m-%d"))
                self.model.add_doc(name=path.basename(file_path), content=content, path=file_path)
        self.update()

    def analyze_button_handler(self):
        method = None
        if self.ui.n_gramm_radioButton.isChecked():
            method = LangRecognMethod.n_gram
        elif self.ui.alphabet_radioButton.isChecked():
            method = LangRecognMethod.alpha
        elif self.ui.neural_radioButton.isChecked():
            method = LangRecognMethod.neural
        doc = self.cur_docs[self.ui.docs_listWidget.currentRow()]
        res = self.model.recognize_text_lang(doc.content, method)
        if self.ui.refresh_statistics_checkBox.isChecked():
            self.model.create_statistics(method)
        self.show_mb("Язык текста документа - " + res.value)

    def view_button_handler(self):
        self.model.show_statistics()

    def show_mb(self, text):
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Icon.Information)
        mb.setWindowTitle("Результат")
        mb.setText(text)
        mb.exec()

    def save_button_handler(self):
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Выберите файл для сохранения", "Satistics.png", "Изображение (*.png);;Все файлы (*.*)", options=QFileDialog.Option.DontUseNativeDialog)
        if file_path:
            self.model.save_statistics_file(file_path)

    @staticmethod
    def link_activated_handler(link_path):
        QDesktopServices.openUrl(link_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()