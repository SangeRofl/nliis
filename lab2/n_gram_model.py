from lang_recog_model import LangRecognModel, Lang
import time
import os
import pickle
import regex as re

class NGramModel(LangRecognModel):
    def __init__(self):
        self.create_en_n_grams()
        self.create_fr_n_grams()

    def create_en_n_grams(self):
        ngrams = dict()
        for filename in os.listdir("./texts/learn_texts/en"):
            with open("./texts/learn_texts/en/" + filename, "rt", encoding="utf8") as f:
                text = f.read().lower()
                words = re.findall(r"\b\p{L}+['\p{L}]+\b", text, flags=re.U)
                for wordl in words:
                    word = " " + wordl + " "
                    for i in range(len(word) - 3 + 1):
                        ngram = word[i:i + 3]
                        if ngram in ngrams.keys():
                            ngrams[ngram] += 1
                        else:
                            ngrams[ngram] = 1
        self.en_n_grams = [i[0] for i in sorted(ngrams.items(), key=lambda x: x[1])[-16:]]

    def create_fr_n_grams(self):
        ngrams = dict()
        for filename in os.listdir("./texts/learn_texts/fr"):
            with open("./texts/learn_texts/fr/" + filename, "rt", encoding="utf8") as f:
                text = f.read().lower()
                words = re.findall(r"\b\p{L}+['\p{L}]+\b", text, flags=re.U)
                for wordl in words:
                    word = " " + wordl + " "
                    for i in range(len(word) - 3 + 1):
                        ngram = word[i:i + 3]
                        if ngram in ngrams.keys():
                            ngrams[ngram] += 1
                        else:
                            ngrams[ngram] = 1
        # print(ngrams)
        self.fr_n_grams = [i[0] for i in sorted(ngrams.items(), key=lambda x: x[1])[-16:]]

    def get_doc_profile(self, text: str):
        ngrams = dict()
        words = re.findall(r"\b\p{L}+['\p{L}]+\b", text, flags=re.U)
        for wordl in words:
            word = " " + wordl + " "
            for i in range(len(word) - 3 + 1):
                ngram = word[i:i + 3]
                if ngram in ngrams.keys():
                    ngrams[ngram] += 1
                else:
                    ngrams[ngram] = 1
        # print(ngrams)
        return [i[0] for i in sorted(ngrams.items(), key=lambda x: x[1])[-16:]]

    def recognize_language(self, text: str):
        file_n_grams = self.get_doc_profile(text)
        fr_dist = self.calc_dist(file_n_grams, self.fr_n_grams)
        en_dist = self.calc_dist(file_n_grams, self.en_n_grams)
        if fr_dist < en_dist:
            return Lang.fr
        else:
            return Lang.en

    @staticmethod
    def calc_dist(prof: list, lang_prof: list):
        dist = 0
        for i in range(len(prof)):
            lang_pos = i
            if prof[i] not in lang_prof:
                dist += len(prof)
                continue
            else:
                prof_pos = lang_prof.index(prof[i])
                dist += abs(lang_pos - prof_pos)
        return dist


if __name__ == "__main__":
    pass
