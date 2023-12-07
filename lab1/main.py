import view
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QCompleter
from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor, QDesktopServices
from PyQt6.QtCore import QStringListModel, Qt, QUrl
import sqlite3
import sys
from pathlib import Path
from os import path
import os
import spacy
from datetime import datetime

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

class Document:
    def __init__(self, name, content, date, doc_id, path):
        self.name = name
        self.content = content
        self.date = date
        self.doc_id = doc_id
        self.path = path

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
    
    def __init__(self, db_name: str = 'docs.db'):
        self.db_docs_conn = sqlite3.connect(db_name)
        self.db_docs_cur = self.db_docs_conn.cursor()
        self.lemmas = []
        self.connect_to_doc_database()
        self.get_lemmas_list()

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

    def get_all_docs(self):
        ids = []
        self.db_docs_cur.execute(f"SELECT id FROM docs;")
        for i in self.db_docs_cur.fetchall():
            ids.append(i[0])
        return self.get_docs(ids)

    def get_doc_from_data(self, data) -> Document:
        return Document(doc_id=data[0], name = data[1], content=data[2], date=data[3], path=data[4])


    def get_lemmas_list(self):
        self.db_docs_cur.execute("SELECT content FROM docs;")
        for item in self.db_docs_cur.fetchall():
            text = item[0].lower()
            doc = nlp(text)
            for token in doc:
                if token.lemma_ not in self.lemmas:
                    self.lemmas.append(token.lemma_.lower())

    def search_docs(self, search_string: str) -> (list, list):
        res = []
        res_words = []
        if search_string == "":
            res = self.get_all_docs()
            res_words = [[] for i in range(len(res))]
        else:
            search_lemm_vects = self.gen_search_lemm_vects(search_text=search_string)
            docs = self.get_all_docs()

            for doc in docs:
                doc_add_flag = True
                for search_lemm_vect in search_lemm_vects:
                    if search_lemm_vect == None:
                        continue
                    doc_lemm_vect = doc.get_lemmas(self.lemmas)
                    flag = True
                    for i in range(len(self.lemmas)):
                        if search_lemm_vect[i] == 1 and doc_lemm_vect[i] == 0:
                            flag = False
                            break
                        elif search_lemm_vect[i] == -1 and doc_lemm_vect[i] == 1:
                            flag = False
                            break
                    if flag and doc not in res:
                        res.append(doc)
                        res_words.append(self.gen_words_to_highlight(search_lemm_vect, doc))

        return res, res_words

    def gen_search_lemm_vects(self, search_text: str) -> list:
        res = []
        search_text=search_text.replace(" AND ", " ")
        search_strings = search_text.split(" OR ")
        search_strings = [i.lower() for i in search_strings]
        for search_string in search_strings:
            search_lemm_vect = []
            search_lemmas = []
            search_not_lemmas = []
            not_flag = False
            for token in nlp(search_string):
                if token.text == "not":
                    not_flag = True
                    continue
                if not_flag:
                    not_flag = False
                    search_not_lemmas.append(token.lemma_)
                if token.lemma_ not in self.lemmas and not_flag == False:
                    search_lemm_vect = None
                    break
                search_lemmas.append(token.lemma_)
            if search_lemm_vect == None:
                res.append(None)
                continue
            for lemma in self.lemmas:
                if lemma in search_lemmas and lemma not in search_not_lemmas:
                    value = 1
                elif lemma in search_lemmas and lemma in search_not_lemmas:
                    value = -1
                else:
                    value = 0
                search_lemm_vect.append(value)
            res.append(search_lemm_vect)
        return res


    def gen_words_to_highlight(self, search_lemm_vect, doc):
        res = []
        doc_tokens = nlp(doc.content)
        search_lemmas = [self.lemmas[i] for i in range(len(self.lemmas)) if search_lemm_vect[i] == 1]
        for token in doc_tokens:
            if token.lemma_.lower() in search_lemmas and token.lemma_.lower() not in res:
                res.append(token.text)
        return res


    def add_doc(self, name, content, path):
        date = datetime.now().strftime("%Y-%m-%d")
        self.db_docs_cur.execute(f"""
                                    INSERT INTO docs(name, content, date, path)
                                    VALUES(?, ?, ?, ?);
                                    """, (name, content, date, path))
        self.db_docs_conn.commit()
        self.get_lemmas_list()

    def get_comleter_list(self):
        return self.lemmas

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
        self.words_to_highlight = []
        self.setup_completer()
        self.ui.label_4.setText('Ссылка на документ')
        self.ui.label_4.setOpenExternalLinks(True)
        self.ui.label_4.linkActivated.connect(self.open_file_explorer)

    def open_file_explorer(self, path):
        QDesktopServices.openUrl(path)



    def setup_completer(self):
        completer_list = self.model.get_comleter_list()
        completer = QCompleter(completer_list, self.ui.search_lineEdit)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.ui.search_lineEdit.setCompleter(completer)
        # self.ui.search_lineEdit.textChanged.connect(self.update_display)

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
        self.cur_docs, self.words_to_highlight = self.model.search_docs(self.ui.search_lineEdit.text())
        self.update()

    def highlight_words_in_text(self, text_container: QWidget, index: int):
        words = self.words_to_highlight[index]
        text = self.cur_docs[index].content
        for word in words:
            start_pos = text.find(word)
            while start_pos != -1:
                self.highlight_text_fragment(self.ui.document_textEdit, start_pos, start_pos+len(word))
                start_pos = text.find(word, start_pos+1)


    def highlight_text_fragment(self, text_container: QWidget, start_pos, end_pos, background_color: QColor = QColor(255, 250, 95, 200)):
            cursor = text_container.textCursor()
            cursor = self.ui.document_textEdit.textCursor()
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
            text_format = QTextCharFormat()
            text_format.setBackground(background_color)
            cursor.mergeCharFormat(text_format)

    def update(self):
        self.update_list()
        self.ui.document_textEdit.clear()

    def update_list(self):
        self.ui.document_listWidget.clear()
        for doc in self.cur_docs:
            self.ui.document_listWidget.addItem(doc.name)


    def docs_list_item_changed_handler(self, index):
        if index != -1:
            content = self.cur_docs[index].content
            self.ui.document_textEdit.setText(content)
            self.highlight_words_in_text(self.ui.document_textEdit, index)
            self.ui.label_4.setText(f'<a href="{path.dirname(self.cur_docs[index].path)}">Ссылка на документ</a>')
        else:
            self.ui.label_4.setText(f'Ссылка на документ')



    def add_doc_button_handler(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Все файлы (*.*)")
        if file_path:
            with open(file_path, "rt") as f:
                content = f.read()
                #print(f.name[:-4], content, datetime.now().strftime("%Y-%m-%d"))
                self.model.add_doc(name=path.basename(file_path), content=content, path = file_path)
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MyMainWindow()
    window.show()

    app.exec()