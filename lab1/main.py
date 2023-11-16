import view
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
import sqlite3
import sys
from pathlib import Path
from os import path
import spacy
from datetime import datetime


class Document:
    def __init__(self, title, text, date, time, doc_id):
        self.title = title
        self.text = text
        self.date = date
        self.time = time
        self.doc_id = doc_id

    def add_doc_to_base(self):
        pass

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = view.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        self.connect_to_doc_database()
        self.ui.add_document_pushButton.clicked.connect(self.add_doc_button_handler)
        self.ui.document_listWidget.currentRowChanged.connect(self.docs_list_item_changed_handler)
        self.ui.search_pushButton.clicked.connect(self.search_button_clicked_handler)
        self.docs_view_indexes = []
        self.lemmas = []
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        self.get_lemmas_list()

    def get_docs(self, indexes):
        self.docs_view_indexes.clear()
        self.ui.document_listWidget.clear()
        ph = ', '.join(['?' for _ in indexes])
        self.db_docs_cur.execute(f"SELECT * FROM docs WHERE id IN ({ph});", indexes)
        for i in self.db_docs_cur.fetchall():
            self.ui.document_listWidget.addItem(i[1])
            self.docs_view_indexes.append(i[0])

    def get_all_docs(self):
        self.docs_view_indexes.clear()
        self.ui.document_listWidget.clear()
        self.db_docs_cur.execute("SELECT * FROM docs;")
        for i in self.db_docs_cur.fetchall():
            self.ui.document_listWidget.addItem(i[1])
            self.docs_view_indexes.append(i[0])

    def search_button_clicked_handler(self):
        self.db_docs_cur.execute("SELECT * FROM docs;")
        if self.ui.search_lineEdit.text() == "":
            self.get_all_docs()
        else:
            res = []
            self.db_docs_cur.execute("SELECT * FROM docs;")
            for item in self.db_docs_cur.fetchall():
                print()
                doc_content = item[2].lower()
                doc_lemmas = [lem.lemma_ for lem in self.nlp(item[2])]
                if self.ui.search_lineEdit.text() in doc_lemmas:
                    res.append(item[0])
            self.get_docs(res)




    def docs_list_item_changed_handler(self, index):
        self.db_docs_cur.execute(f"SELECT content from docs WHERE id={self.docs_view_indexes[index]};")
        content = self.db_docs_cur.fetchall()[0][0]
        self.ui.document_textEdit.setText(content)

    def connect_to_doc_database(self):
        self.db_docs_conn = sqlite3.connect(r'docs.db')
        self.db_docs_cur = self.db_docs_conn.cursor()
        self.db_docs_cur.execute("""
        CREATE TABLE IF NOT EXISTS docs(
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           name TEXT,
           content TEXT,
           date TEXT);
        """)
        self.db_docs_conn.commit()
        self.db_docs_cur.execute("SELECT * FROM docs;")

    def add_doc_button_handler(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Все файлы (*.*)")
        if file_path:
            with open(file_path, "rt") as f:
                content = f.read()
                #print(f.name[:-4], content, datetime.now().strftime("%Y-%m-%d"))
                self.db_docs_cur.execute(f"""
                            INSERT INTO docs(name, content, date)
                            VALUES(?, ?, ?);
                            """, (path.basename(file_path), content, datetime.now().strftime("%Y-%m-%d")))
                self.db_docs_conn.commit()


    def get_lemmas_list(self):
        self.db_docs_cur.execute("SELECT content FROM docs;")
        for item in self.db_docs_cur.fetchall():
            doc = self.nlp(item[0])
            for token in doc:
                if token.lemma_.lower() not in self.lemmas:
                    self.lemmas.append(token.lemma_.lower())




if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MyMainWindow()
    window.show()

    app.exec()
