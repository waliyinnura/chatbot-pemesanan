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
from sklearn.metrics import classification_report

# normalized_docs = []
# test_docs = [
#         (["saya", "ingin", "memesan"], "pesan"),
#         (["lihat", "menu", "makanan"], "gambarMenu"),
#         (["saya", "ingin", "membayar"], "pembayaran"),
#         # ([], "terimaKasih"),
#         # ([], "greetingsPagi"),
#         # ([], "greetingsSiang"),
#         # ([], "greetingsSore"),
#         # ([], "greetingsMalam"),
#         # ([], "greetingsMuslim"),
#         # ([], "greetingsKatolik"),
#         # ([], "greetingsProtestan"),
#         # ([], "greetingsHindu"),
#         # ([], "greetingsKhonghucu"),
#         # ([], "greetingsBuddha"),
#         # ([], "menuRekomendasi")
#     ]

def evaluate_model(model, words, classes, word_counts, normalized_docs):
    test_docs = [
        (["saya", "ingin", "memesan"], "pesan"),
        (["lihat", "menu", "makanan"], "gambarMenu"),
        (["saya", "ingin", "membayar"], "pembayaran"),
        (["terima", "kasih"], "terimaKasih"),
        (["selamat", "pagi"], "greetingsPagi"),
        (["selamat", "siang"], "greetingsSiang"),
        (["selamat", "sore"], "greetingsSore"),
        (["selamat", "malam"], "greetingsMalam"),
        (["assalamualaikum"], "greetingsMuslim"),
        (["salam", "sejahtera"], "greetingsKatolik"),
        (["shalom"], "greetingsProtestan"),
        (["om", "swastiyastu"], "greetingsHindu"),
        (["wei", "de", "dong", "tian"], "greetingsKhonghucu"),
        (["namo", "buddhaya"], "greetingsBuddha"),
        (["apa", "menu", "rekomendasi", "disini"], "menuRekomendasi"),
        (["apakah", "makanan", "disini", "halal"], "makananHalal"),
        (["saran", "makanan", "favorit"], "makananSignature"),
        (["makanan", "untuk", "vegan"], "menuVegan"),
        (["menyiapkan", "makanannya"], "waktuPemesanan"),
        (["kapan", "restoran", "buka", "bro"], "jamOperasional"),
        (["apakah", "makanan", "disini", "boleh", "dibungkus"], "takeAway"),
        (["sarankan", "makanan", "untuk", "anak"], "menuAnak"),
        (["makanan", "yang", "cocok", "untuk", "keluarga"], "hidanganKelompok"),
        (["kapan", "dianternya", "nih"], "lamaMenunggu"),
        (["halo", "bro"], "greetings"),
        (["ayam", "bakar", "taliwang"], "menu"),
        # Variasi tambahan
        (["bagaimana", "cara", "pesan"], "pesan"),
        (["tampilkan", "daftar", "menu"], "gambarMenu"),
        (["bagaimana", "membayar", "pesanan"], "pembayaran"),
        (["terima", "kasih", "sekali"], "terimaKasih"),
        (["hai", "pagi"], "greetingsPagi"),
        (["hai", "siang"], "greetingsSiang"),
        (["hai", "sore"], "greetingsSore"),
        (["selamat", "malam", "juga"], "greetingsMalam"),
        (["hai", "kak", "apa", "kabar"], "greetingsMuslim"),
        (["selamat", "sejahtera", "juga"], "greetingsKatolik"),
        (["hello"], "greetingsProtestan"),
        (["om", "swastiyastu", "juga"], "greetingsHindu"),
        (["wei", "de", "dong", "tian", "juga"], "greetingsKhonghucu"),
        (["namo", "buddhaya", "juga"], "greetingsBuddha"),
        (["rekomendasi", "apa", "yang", "terbaik"], "menuRekomendasi"),
        (["adakah", "menu", "halal"], "makananHalal"),
        (["menu", "favorit", "apa", "yang", "kamu", "sarankan"], "makananSignature"),
        (["saya", "vegan"], "menuVegan"),
        (["berapa", "lama", "pesanan", "siap"], "waktuPemesanan"),
        (["jam", "operasional", "restoran"], "jamOperasional"),
        (["bisakah", "saya", "mengambil", "pesanan"], "takeAway"),
        (["menu", "apa", "yang", "cocok", "untuk", "anak-anak"], "menuAnak"),
        (["menu", "kelompok", "apa", "yang", "kamu", "sugestikan"], "hidanganKelompok"),
        (["berapa", "lama", "waktu", "pengantaran"], "lamaMenunggu"),
        (["hai", "bro"], "greetings"),
        (["pesen", "ayam", "bakar", "taliwang"], "menu")
    ]

    test_x = []
    test_y = []
    out = [0] * len(classes)

    for doc in test_docs:
        bag = []
        word_patterns = doc[0]
        for word in words:
            bag.append(word_counts[word]) if word in word_patterns else bag.append(0)
        out_row = list(out)
        out_row[classes.index(doc[1])] = 1
        test_x.append(bag)
        test_y.append(out_row)

    test_x = np.array(test_x)
    test_y = np.array(test_y)

    predictions = model.predict(test_x)
    predicted_labels = [classes[np.argmax(prediction)] for prediction in predictions]
    actual_labels = [classes[np.argmax(label)] for label in test_y]

    report = classification_report(actual_labels, predicted_labels)
    print("Laporan Evaluasi Out-of-Sample:")
    # print("test_x: ", test_x)
    # print("test_y: ", test_y)
    # exit()
    print(report)

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

    # print("train x: ", train_x)
    # print("train y: ", train_y)
    # exit()
    # print("val x: ", val_x)
    # print("val y: ", val_y)

    # Model Neural Network
    model = Sequential()
    model.add(Dense(256, input_shape=(len(train_x[0]),), activation='relu'))
    # print(len(train_x[0]))
    model.add(Dropout(0.2))
    model.add(Dense(128))
    model.add(Dense(64, activation='relu'))
    # model.add(Dropout(0.4))

    # Jumlah neuron output disesuaikan dengan jumlah kelas (classes)
    model.add(Dense(len(classes), activation='softmax'))
    # print(len(classes))
    # exit()
    sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
    
    # membuat model dan save model
    try:
        hist = model.fit(np.array(train_x), np.array(train_y), epochs=378, batch_size=32, verbose=1)
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

        evaluate_model(model, words, classes, word_counts, normalized_docs)
        # print(test_docs)
        # print(normalized_docs)
    else:
        print("Pelatihan Model Gagal!")

if __name__ == "__main__":
    trains()