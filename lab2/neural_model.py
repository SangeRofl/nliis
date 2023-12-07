from lang_recog_model import LangRecognModel, Lang
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import keras
import os
import pickle



class NeuralModel(LangRecognModel):
    def __init__(self):
        with open("neural_data.pkl", "rb") as f:
            data = pickle.load(f)

        self.model, self.max_len, self.labels = data[0], data[1], data[2]

    def recognize_language(self, text: str):
        tokenizer = Tokenizer()
        print(text)
        new_sequences = tokenizer.texts_to_sequences([text])
        new_padded_sequences = pad_sequences(new_sequences, maxlen=self.max_len)
        predictions = self.model.predict(new_padded_sequences)
        predicted_labels = [self.labels[prediction.argmax()] for prediction in predictions]
        print(predicted_labels[0])
        if predicted_labels[0] == Lang.fr.value:
            return Lang.fr
        else:
            return Lang.en


if __name__ == "__main__":
    texts = []
    labels = []
    en_texts_names = os.listdir("texts/learn_texts/en")
    for text_name in en_texts_names:
        with open("texts/learn_texts/en/"+text_name, "rt", encoding="utf-8") as f:
            text = f.read()
            texts.append(text)
            labels.append(Lang.en.value)
    fr_texts_names = os.listdir("texts/learn_texts/fr")
    for text_name in fr_texts_names:
        with open("texts/learn_texts/fr/"+text_name, "rt", encoding="utf-8") as f:
            text = f.read()
            texts.append(text)
            labels.append(Lang.fr.value)

    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(texts)
    word_index = tokenizer.word_index

    sequences = tokenizer.texts_to_sequences(texts)

    max_length = max(len(seq) for seq in sequences)
    padded_sequences = pad_sequences(sequences, maxlen=max_length).tolist()

    label_mapping = {label: i for i, label in enumerate(labels)}
    numeric_labels = [label_mapping[label] for label in labels]

    model = keras.Sequential([
        keras.layers.Embedding(len(word_index) + 1, 100, input_length=max_length),
        keras.layers.Conv1D(128, 5, activation='relu'),
        keras.layers.GlobalMaxPooling1D(),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(len(labels), activation='softmax')
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(padded_sequences, numeric_labels, epochs=1000)
    with open("neural_data.pkl", "wb") as file:
        pickle.dump([model, max_length, labels], file)
    new_texts = ['En anglais un même mot peut prendre un sens différent selon le contexte. Si tu veux écrire en chinois, il faut connaître des milliers d’idiogrammes. Et pour un Européen il est presque impossible de produire les clics du xhosa, une des langues africaines.']
    new_sequences = tokenizer.texts_to_sequences(new_texts)
    new_padded_sequences = pad_sequences(new_sequences, maxlen=max_length)
    predictions = model.predict(new_padded_sequences)
    predicted_labels = [labels[prediction.argmax()] for prediction in predictions]
    print(predicted_labels)
