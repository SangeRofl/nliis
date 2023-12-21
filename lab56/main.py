from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QMainWindow, QCompleter, QFileDialog
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import sys
from source.view import Ui_MainWindow
from source.model import Document, Model, Lang
from os import path, remove
import speech_recognition as sr
import random


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        self.model = Model("source/data/docs.sqlite3")
        self.cur_docs = []
        self.last_search = ""
        self.words_to_highlight = []
        self.setup_completer()
        self.ui.link_label.setText('Ссылка на документ')
        self.ui.link_label.setOpenExternalLinks(True)
        self.connect_signals()
        self.cur_docs = self.model.get_all_docs()
        self.update()
        self.get_actions()
        self.get_voices()

    def connect_signals(self):
        self.ui.add_pushButton.clicked.connect(self.add_doc_button_handler)
        self.ui.docs_listWidget.currentRowChanged.connect(self.docs_list_item_changed_handler)
        self.ui.search_pushButton.clicked.connect(self.search_button_clicked_handler)
        self.ui.del_pushButton.clicked.connect(self.del_doc_button_handler)
        self.ui.link_label.linkActivated.connect(self.open_file_explorer)
        self.ui.voice_pushButton.clicked.connect(self.voice_button_handler)
        self.ui.en_radioButton.clicked.connect(self.en_radio_button_handler)
        self.ui.ru_radioButton.clicked.connect(self.ru_radio_button_handler)
        self.ui.send_pushButton.clicked.connect(self.send_button_handler)
        self.ui.volume_verticalSlider.valueChanged.connect(self.volume_slider_handler)
        self.ui.speed_verticalSlider.valueChanged.connect(self.speed_slider_handler)
        self.ui.voice_type_comboBox.currentTextChanged.connect(self.voice_type_combo_box_handler)
        self.ui.tts_pushButton.clicked.connect(self.tts_button_handler)
        self.ui.stop_pushButton.clicked.connect(self.stop_button_handler)

    def stop_button_handler(self):
        self.model.stop_speech()

    def get_actions(self):
        for action in self.model.actions:
            self.ui.commands_listWidget.addItem(action.name)

    def get_voices(self):
        for voice in self.model.voices:
            self.ui.voice_type_comboBox.addItem(voice)

    def volume_slider_handler(self, value):
        self.model.voice_volume = value/100

    def voice_type_combo_box_handler(self, text):
        self.model.cur_voice_name = text

    def speed_slider_handler(self, value):
        self.model.voice_rate = value

    def add_doc_button_handler(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Все файлы (*.*)")
        if file_path:
            with open(file_path, "rt", encoding="utf-8") as f:
                content = f.read()
                # print(f.name[:-4], content, datetime.now().strftime("%Y-%m-%d"))
                self.model.add_doc(name=path.basename(file_path), content=content, path=file_path)
        self.update()

    def send_button_handler(self):
        message_text = self.ui.chat_lineEdit.text()
        self.handle_action(*self.model.get_text_message_action(message_text))

    def tts_button_handler(self):
        self.model.text_to_speech(self.ui.doc_textEdit.toPlainText())

    def do_action(self, action_id, data):
        reply_text = ""
        if action_id == 0:
            self.search_docs(" ".join(data))
            if self.model.lang == Lang.ru:
                reply_text = random.choice(self.model.actions[action_id].ru_answers)
            else:
                reply_text = random.choice(self.model.actions[action_id].en_answers)
        elif action_id == -1:
            if self.model.lang == Lang.ru:
                reply_text = "Не удалось распознать запрос"
            else:
                reply_text = "Could not recognize request"
        elif action_id == 1:
            if self.model.lang == Lang.ru:
                reply_text = random.choice(self.model.actions[action_id].ru_answers)
            else:
                reply_text = random.choice(self.model.actions[action_id].en_answers)
            reply_text += " "+self.ui.doc_textEdit.toPlainText()
        elif action_id == 2:
            if self.model.lang == Lang.ru:
                reply_text = random.choice(self.model.actions[action_id].ru_answers)
            else:
                reply_text = random.choice(self.model.actions[action_id].en_answers)
        elif action_id == 3:
            if self.model.lang == Lang.ru:
                reply_text = random.choice(self.model.actions[action_id].ru_answers)
            else:
                reply_text = random.choice(self.model.actions[action_id].en_answers)
            if self.ui.docs_listWidget.currentRow() == -1:
                if self.model.lang == Lang.ru:
                    reply_text = "Вы не выбрали документ для удаления"
                else:
                    reply_text = "You didn't choose the document for deletion"
            self.del_doc_button_handler()
        try:
            remove('temp.wav')
        except:
            print("deletion canceled")
        self.model.text_to_speech(reply_text)
        #self.startMusic()
        self.write_chat(0, reply_text)

    def startMusic(self):
        # Создание объекта QMediaPlayer и установка аудиофайла
        self.player = QMediaPlayer()
        self.auot = QAudioOutput()
        self.auot.setVolume(50)
        self.player.setAudioOutput(self.auot)
        self.player.setSource(QUrl.fromLocalFile('temp.wav'))
        self.player.play()  # Воспроизведение музыки



    def en_radio_button_handler(self):
        if self.ui.en_radioButton.isChecked():
            self.model.set_lang(Lang.en)

    def ru_radio_button_handler(self):
        if self.ui.ru_radioButton.isChecked():
            self.model.set_lang(Lang.ru)

    def voice_button_handler(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
        self.handle_action(*self.model.get_audio_message_action(audio))

    def handle_action(self, text, action_id, data):
        self.write_chat(1, text)
        self.do_action(action_id, data)

    def write_chat(self, is_user: bool|int, text: str):
        if is_user:
            speaker = "User"
        else:
            speaker = "Helper"
        self.ui.chat_textEdit.append(f"{speaker}:\n{text}\n")
        self.ui.chat_textEdit.ensureCursorVisible()

    def search_docs(self, text: str):
        self.last_search = text
        self.update()

    def search_button_clicked_handler(self):
        self.search_docs(self.ui.search_lineEdit.text())

    def del_doc_button_handler(self):
        if self.ui.docs_listWidget.currentRow() >= 0:
            self.model.del_doc(self.cur_docs[self.ui.docs_listWidget.currentRow()].doc_id)
            self.update()

    def update(self):
        self.cur_docs, self.words_to_highlight = self.model.search_docs(self.last_search)
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