import view
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
import sqlite3
import sys
from pathlib import Path
from os import path
import spacy
from datetime import datetime

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

class Document:
    def __init__(self, name, content, date, doc_id):
        self.name = name
        self.content = content
        self.date = date
        self.doc_id = doc_id

    def get_lemmas(self, ful_lemmas):
        text = self.content.lower()
        doc = nlp(text)
        doc_lemmas = []
        for token in doc:
            doc_lemmas.append(token.lemma_)
        res = []
        for lemma in ful_lemmas:
            res.append(1 if lemma in doc_lemmas else 0)
        return res

class Model:
    def __init__(self):
        self.lemmas = []
        self.connect_to_doc_database()
        self.get_lemmas_list()

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

    def get_docs(self, indexes):
        res = []
        ph = ', '.join(['?' for _ in indexes])
        self.db_docs_cur.execute(f"SELECT * FROM docs WHERE id IN ({ph});", indexes)
        for i in self.db_docs_cur.fetchall():
            res.append(self.get_doc_from_data(i))
        return res

    def get_all_docs(self):
        ids = []
        self.db_docs_cur.execute(f"SELECT id FROM docs;")
        for i in self.db_docs_cur.fetchall():
            ids.append(i[0])
        return self.get_docs(ids)

    def get_doc_from_data(self, data) -> Document:
        return Document(doc_id=data[0], name = data[1], content=data[2], date=data[3])


    def get_lemmas_list(self):
        self.db_docs_cur.execute("SELECT content FROM docs;")
        for item in self.db_docs_cur.fetchall():
            text = item[0].lower()
            doc = nlp(text)
            for token in doc:
                if token.lemma_ not in self.lemmas:
                    self.lemmas.append(token.lemma_.lower())

    def search_docs(self, search_string: str) -> list:
        res = []
        if search_string == "":
            return self.get_all_docs()
        else:
            search_string = search_string.lower()
            search_lemm_vect = []
            search_lemmas = []
            for token in nlp(search_string):
                search_lemmas.append(token.lemma_)
            for lemma in self.lemmas:
                search_lemm_vect.append(1 if lemma in search_lemmas else 0)

            docs = self.get_all_docs()
            for doc in docs:
                doc_lemm_vect = doc.get_lemmas(self.lemmas)
                flag = True
                for i in range(len(self.lemmas)):
                    if search_lemm_vect[i] == 1 and doc_lemm_vect[i] == 0:
                        flag = False
                        break
                if flag:
                    res.append(doc)
        return res


    def add_doc(self, name, content):
        date = datetime.now().strftime("%Y-%m-%d")
        self.db_docs_cur.execute(f"""
                                    INSERT INTO docs(name, content, date)
                                    VALUES(?, ?, ?);
                                    """, (name, content, date))
        self.db_docs_conn.commit()
        self.get_lemmas_list()

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model = Model()
        self.ui = view.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        self.ui.add_document_pushButton.clicked.connect(self.add_doc_button_handler)
        self.ui.document_listWidget.currentRowChanged.connect(self.docs_list_item_changed_handler)
        self.ui.search_pushButton.clicked.connect(self.search_button_clicked_handler)
        self.cur_docs = []



    def search_button_clicked_handler(self):
        # self.db_docs_cur.execute("SELECT * FROM docs;")
        # if self.ui.search_lineEdit.text() == "":
        #     self.get_all_docs()
        # else:
        #     res = []
        #     self.db_docs_cur.execute("SELECT * FROM docs;")
        #     for item in self.db_docs_cur.fetchall():
        #         print()
        #         doc_content = item[2].lower()
        #         doc_lemmas = [lem.lemma_ for lem in self.nlp(item[2])]
        #         if self.ui.search_lineEdit.text() in doc_lemmas:
        #             res.append(item[0])
        #     self.get_docs(res)
        self.cur_docs = self.model.search_docs(self.ui.search_lineEdit.text())
        self.update()

    def update(self):
        self.update_list()

    def update_list(self):
        self.ui.document_listWidget.clear()
        for doc in self.cur_docs:
            self.ui.document_listWidget.addItem(doc.name)


    def docs_list_item_changed_handler(self, index):
        if index != -1:
            content = self.cur_docs[index].content
            self.ui.document_textEdit.setText(content)



    def add_doc_button_handler(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Все файлы (*.*)")
        if file_path:
            with open(file_path, "rt") as f:
                content = f.read()
                #print(f.name[:-4], content, datetime.now().strftime("%Y-%m-%d"))
                self.model.add_doc(name=path.basename(file_path), content=content)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MyMainWindow()
    window.show()

    app.exec()