import speech_recognition as sr
import pyaudio
import wave
from gtts import gTTS
import sqlite3
import spacy
from enum import Enum
import pyttsx3
import random
from pydub import AudioSegment
import wave

nlp = spacy.load("en_core_web_sm")
nlp_ru = spacy.load("ru_core_news_sm")

class Lang(Enum):
    ru = "ru"
    en = "en"


class Action:
    def __init__(self, name, ru_examples:list = [], en_examples:list = [], ru_answers:list = [], en_answers:list = []):
        self.name = name
        self.ru_examples = ru_examples
        self.en_examples = en_examples
        self.ru_answers = ru_answers
        self.en_answers = en_answers

class Document:
    def __init__(self, name, content, doc_id, path):
        self.name = name
        self.content = content
        self.doc_id = doc_id
        self.path = path

    def get_lemmas(self):
        text = self.content.lower()
        doc = nlp(text)
        doc_lemmas = []
        for token in doc:
            doc_lemmas.append(token.lemma_)
        return doc_lemmas


class Model:
    def __init__(self, db_filename="./data/docs.sqlite3"):
        self.db_docs_conn = sqlite3.connect(db_filename)
        self.db_docs_cur = self.db_docs_conn.cursor()
        self.connect_to_doc_database()
        self.lemmas = []
        self.get_lemmas_list()
        self.lang = Lang.en
        self.create_actions()
        self.voices = dict()
        self.voice_rate = 150
        self.voice_volume = 1
        self.cur_voice_name = ""
        self._nlp = nlp
        self._sr_lang = "en-US"
        self.find_voices()

    def create_actions(self):
        self.actions = []
        self.actions.append(Action("Поиск по словам", [
            "найди документ в котором есть слова",
            "найди документ со словами",
            "в каком документе встречаются слова",
        ], [
            "find a document with word",
            "search a document with words"
        ], [
            "Вот список документов, в которых встречаются данные слова"
        ], [
            "Here is a list of documets with these words"
        ]))
        self.actions.append(Action("Чтение документа", [
            "Прочитай мне этот документ",
            "Что написано в этом документе",
        ], [
                                       "Read me this document",
                                       "Could you read me this document"
                                   ], [
                                       "В этом документе написано"
                                   ], [
                                       "This document says"
                                   ]))
        self.actions.append(Action("Приветствие", [
            "Привет",
            "Здравствуйте",
            "Хай",
        ], [
                                       "Hello",
                                       "Greetings"
                                   ], [
                                       "Здравствуйте",
                                        "Приветствую вас, уважаемый",
                                   ], [
                                       "Hello",
                                        "Nice to see you",
                                   ]))
        self.actions.append(Action("Удаление документа", [
            "Удали этот документ",
            "Уничтожь этот документ",
            "Удали выбранный документ",
        ], [
                                       "Delete this document",
                                       "remove the document"
                                   ], [
                                       "Документ был удален",
                                       "Хорошо",
                                   ], [
                                       "The document was deleted",
                                       "Ok",
                                   ]))

    def find_voices(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "Russian" in voice.name or "English" in voice.name:
                self.voices[voice.name] = voice.id
        self.cur_voice_name = list(self.voices.keys())[0]

    def stop_speech(self):
        self.engine.stop()
    def text_to_speech(self, text: str):
        self.engine.setProperty("voice", self.voices[self.cur_voice_name])
        self.engine.setProperty("rate", self.voice_rate)
        self.engine.setProperty("volume", self.voice_volume)
        print(self.engine.getProperty("voice"))
        print(self.engine.getProperty("rate"))
        print(self.engine.getProperty("volume"))
        #self.engine.save_to_file(text, "temp.wav")
        # audio = AudioSegment.from_file_using_temporary_files(buf)
        # audio.export("temp.wav", format="wav")
        self.engine.say(text)
        self.engine.runAndWait()
        #audio.export("voice.mp3", format="mp3")

    def get_lemmas_list(self):
        self.db_docs_cur.execute("SELECT content FROM docs;")
        for item in self.db_docs_cur.fetchall():
            text = item[0].lower()
            doc = nlp(text)
            for token in doc:
                if token.lemma_ not in self.lemmas:
                    self.lemmas.append(token.lemma_.lower())

    def connect_to_doc_database(self):
        self.db_docs_cur.execute("""
                CREATE TABLE IF NOT EXISTS docs(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT,
                   content TEXT,
                   path TEXT);
                """)

    def get_text_message_action(self, text):
        action_id = self.recognize_action(text)
        data = self.get_action_data(action_id, text)
        return text, action_id, data

    def get_audio_message_action(self, audio):
        r = sr.Recognizer()
        try:
            text = r.recognize_google(audio, language=self._sr_lang).lower()
        except:
            text = ""
        return self.get_text_message_action(text)

    def recognize_action(self, command_text: str) -> int:
        command_text = command_text.lower()
        if len(command_text)!= 0 and not command_text[-1].isalnum():
            command_text = command_text[:-1]
        command_lemmas = {word.lemma_ for word in self._nlp(command_text)}
        for action_id in range(len(self.actions)):
            examples = self.actions[action_id].ru_examples if self.lang == Lang.ru else self.actions[action_id].en_examples
            for example in examples:
                example_lemmas = {word.lemma_ for word in self._nlp(example)}
                example_len = len(example_lemmas)
                satisf_lem_count = 0
                for command_lemma in command_lemmas:
                    if command_lemma in example_lemmas:
                        satisf_lem_count+=1
                if satisf_lem_count/example_len > 0.60:
                    return action_id
        return -1

    def get_action_data(self, action_id, text):
        data = []
        if action_id == 0:
            if self.lang == Lang.en:
                last_action_lemma = [word.lemma_ for word in nlp("word")][0]
            else:
                last_action_lemma = [word.lemma_ for word in nlp_ru("слово")][0]
            text_doc = self._nlp(text)
            data_flag = False
            for token in text_doc:
                if data_flag:
                    data.append(token.text)
                    continue
                if token.lemma_==last_action_lemma:
                    data_flag = True
        elif action_id == -1:
            return data
        elif action_id in (1, 2, 3):
            pass
        return data

    def get_docs(self, indexes):
        res = []
        ph = ', '.join(['?' for _ in indexes])
        self.db_docs_cur.execute(f"SELECT * FROM docs WHERE id IN ({ph});", indexes)
        for i in self.db_docs_cur.fetchall():
            res.append(self.get_doc_from_data(i))
        return res

    def get_completer_list(self):
        return self.lemmas

    def set_lang(self, lang):
        if lang == Lang.en:
            self._nlp = nlp
            self.lang = Lang.en
            self._sr_lang = "en-US"
        else:
            self._nlp = nlp_ru
            self.lang = Lang.ru
            self._sr_lang = "ru-RU"


    def add_doc(self, name, content, path):
        self.db_docs_cur.execute(f"""
                                    INSERT INTO docs(name, content, path)
                                    VALUES(?, ?, ?);
                                    """, (name, content, path))
        self.db_docs_conn.commit()

    def del_doc(self, index):
        self.db_docs_cur.execute(f"DELETE FROM docs WHERE id = {index};")
        self.db_docs_conn.commit()

    @staticmethod
    def get_doc_from_data(data) -> Document:
        return Document(doc_id=data[0], name=data[1], content=data[2], path=data[3])

    def get_all_docs(self):
        ids = []
        self.db_docs_cur.execute(f"SELECT id FROM docs;")
        for i in self.db_docs_cur.fetchall():
            ids.append(i[0])
        return self.get_docs(ids)

    def search_docs(self, search_string: str) -> (list, list):
        res = []
        res_words = []
        if search_string == "":
            res = self.get_all_docs()
            res_words = [[] for i in range(len(res))]
        else:
            docs = self.get_all_docs()
            search_doc = nlp(search_string.lower())
            search_lemmas = [word.lemma_ for word in search_doc]
            for doc in docs:
                doc_add_flag = True
                doc_lemm_vect = doc.get_lemmas()
                for search_lemma in search_lemmas:
                    if search_lemma not in doc_lemm_vect:
                        doc_add_flag = False
                        break
                if doc_add_flag:
                    res.append(doc)
                    res_words.append(search_lemmas)

        return res, res_words



if __name__ == "__main__":
    engine = pyttsx3.init()

    # Получение доступных голосов
    voices_ = engine.getProperty('voices')

    # Вывод списка доступных голосов
    print("Доступные голоса:")
    for voice_ in voices_:
        print(f"ID: {voice_.id}")
        print(f"Имя: {voice_.name}")
        print(f"Язык: {voice_.languages}")
        print(f"Пол: {voice_.gender}")
        print(f"Возраст: {voice_.age}")
        print("------------")
    engine.setProperty("rate", 100)
    engine.say("Привет мир")
    engine.runAndWait()
    engine.setProperty("rate", 200)
    engine.say("Привет мир")
    engine.runAndWait()