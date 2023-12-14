import speech_recognition as sr
import pyaudio
import wave
from gtts import gTTS
import sqlite3

class Document:
    def __init__(self, name, content, doc_id, path):
        self.name = name
        self.content = content
        self.doc_id = doc_id
        self.path = path


class Model:
    def __init__(self):
        pass

    def connect_to_db(self, db_filename="./data/docs.sqlite3"):
        self.db_docs_conn = sqlite3.connect(db_filename)
        self.db_docs_cur = self.db_docs_conn.cursor()
        self.connect_to_doc_database()

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

    def add_doc(self, name, content, path):
        self.db_docs_cur.execute(f"""
                                    INSERT INTO docs(name, content, path)
                                    VALUES(?, ?, ?, ?);
                                    """, (name, content, path))
        self.db_docs_conn.commit()

    @staticmethod
    def get_doc_from_data(data) -> Document:
        return Document(doc_id=data[0], name=data[1], content=data[2], path=data[3])

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
