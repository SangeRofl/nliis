import speech_recognition as sr
import pyaudio
import wave
from gtts import gTTS
import sqlite3
import spacy

nlp = spacy.load("en_core_web_sm")

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

    def get_docs(self, indexes):
        res = []
        ph = ', '.join(['?' for _ in indexes])
        self.db_docs_cur.execute(f"SELECT * FROM docs WHERE id IN ({ph});", indexes)
        for i in self.db_docs_cur.fetchall():
            res.append(self.get_doc_from_data(i))
        return res

    def get_completer_list(self):
        return self.lemmas

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
                doc_lemm_vect = doc.get_lemmas(self.lemmas)
                for search_lemma in search_lemmas:
                    if search_lemma not in doc_lemm_vect:
                        doc_add_flag = False
                        break
                if doc_add_flag:
                    res.append(doc)
                    res_words.append(search_lemmas)

        return res, res_words


# def record_audio(file_name, duration):
#     chunk = 1024
#     format = pyaudio.paInt16
#     channels = 1
#     rate = 44100
#
#     p = pyaudio.PyAudio()
#
#     stream = p.open(format=format,
#                     channels=channels,
#                     rate=rate,
#                     input=True,
#                     frames_per_buffer=chunk)
#
#     print("Recording started...")
#
#     frames = []
#
#     for i in range(int(rate / chunk * duration)):
#         data = stream.read(chunk)
#         frames.append(data)
#
#     print("Recording finished.")
#
#     stream.stop_stream()
#     stream.close()
#     p.terminate()
#
#     wf = wave.open(file_name, 'wb')
#     wf.setnchannels(channels)
#     wf.setsampwidth(p.get_sample_size(format))
#     wf.setframerate(rate)
#     wf.writeframes(b''.join(frames))
#     wf.close()
#
#
#
#
# if __name__ == "__main__":
#     # record_audio("test1.wav", 4)
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Говорите...")
#         audio = recognizer.listen(source)
#     # audio_file = sr.AudioFile("test1.wav")
#     # with audio_file as source:
#     #     audio_data = recognizer.record(source)
#     #     text = recognizer.recognize_google(audio_data)
#     text = recognizer.recognize_google(audio)
#     tts = gTTS(text, slow = False)
#     tts.save("sinth.mp3")
#     # Выводим текст
#     print(text)
