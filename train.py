from collections import Counter, defaultdict
import numpy as np
import pickle
import json
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.python.keras.layers import Dense, Dropout
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.optimizer_v2.gradient_descent import SGD
from tensorflow.python.keras.models import save_model
from patterns import responsepatterns
import matplotlib.pyplot as plt

def trains():
    # Preprocessing
    lemmatizer = WordNetLemmatizer()
    intents = json.loads(responsepatterns.text)

    words = []
    classes = []
    docs = []
    ignore_list = ['?', '!', '.', ',', "'"]

    for intent in intents['intents']:
        for pattern in intent['patterns']:
            word_list = nltk.word_tokenize(pattern)
            words.extend(word_list)
            docs.append((word_list, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    # Normalisasi kata dan pengumpulan dokumen
    normalized_docs = []
    word_counts = Counter()

    for doc in docs:
        word_patterns = [lemmatizer.lemmatize(word.lower()) for word in doc[0] if word not in ignore_list]
        normalized_docs.append((word_patterns, doc[1]))
        word_counts.update(word_patterns)

    # Membangun kamus kata unik
    words = sorted(set(words))
    classes = sorted(set(classes))

    # Membangun kamus kata dengan frekuensi
    word_counts = defaultdict(int, word_counts)

    # Menyimpan kamus kata dan kelas
    pickle.dump(words, open("datas/words.pkl", "wb"))
    pickle.dump(classes, open("datas/classes.pkl", "wb"))

    training = []
    out = [0] * len(classes)

    # Representasi bag-of-words
    for doc in normalized_docs:
        bag = []
        word_patterns = doc[0]
        for word in words:
            bag.append(word_counts[word]) if word in word_patterns else bag.append(0)

        out_row = list(out)
        out_row[classes.index(doc[1])] = 1
        training.append([bag, out_row])

    np.random.shuffle(training)
    training = np.array(training)

    train_x = list(training[:, 0])
    train_y = list(training[:, 1])

    # Model Neural Network
    model = Sequential()
    model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))

    # Jumlah neuron output disesuaikan dengan jumlah kelas (classes)
    model.add(Dense(len(classes), activation='softmax'))

    sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

    try:
        hist = model.fit(np.array(train_x), np.array(train_y), epochs=800, batch_size=5, verbose=1)
        model.save("chatbot_model.h5")
        print("Model saved as chatbot_model.h5")
    except Exception as e:
        print("Terjadi kesalahan saat melatih model:", str(e))

    if 'hist' in locals():
        # Plot grafik akurasi
        plt.plot(hist.history['accuracy'])
        plt.title('Model Accuracy')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.show()

        # Plot grafik loss
        plt.plot(hist.history['loss'])
        plt.title('Model Loss')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.show()

        # Rata-rata akurasi
        avg_accuracy = np.mean(hist.history['accuracy'])
        print("Rata-rata akurasi (Training):", avg_accuracy)

        # Rata-rata loss
        avg_loss = np.mean(hist.history['loss'])
        print("Rata-rata loss (Training):", avg_loss)

        print("Pelatihan selesai!")
    else:
        print("Pelatihan model gagal.")
trains()