import json
import nltk
import numpy
import pickle
import matplotlib.pyplot as plt

from nltk.stem import WordNetLemmatizer
from tensorflow.python.keras.layers import Dense, Dropout
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.optimizer_v2.gradient_descent import SGD
from patterns import responsepatterns

def training(responsepatterns):
    lemmatizer = WordNetLemmatizer()
    intents = json.loads(responsepatterns.text)
    print(intents)

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

    words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_list]
    words = sorted(set(words))
    classes = sorted(set(classes))
    print(words)

    pickle.dump(words, open("datas/words.pkl", "wb"))
    pickle.dump(classes, open("datas/classes.pkl", "wb"))

    training = []
    out = [0] * len(classes)

    for doc in docs:
        bag = []
        word_patterns = doc[0]
        word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
        for word in words:
            if word in word_patterns:
                bag.append(1)
            else:
                bag.append(0)

        out_row = list(out)
        out_row[classes.index(doc[1])] = 1
        training.append([bag, out_row])

    numpy.random.shuffle(training)
    training = numpy.array(training)

    train_x = list(training[:, 0])
    train_y = list(training[:, 1])

    model = Sequential()
    model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))

    model.add(Dense(len(train_y[0]), activation='softmax'))
    sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

    hist = model.fit(numpy.array(train_x), numpy.array(train_y), epochs=400, batch_size=5, verbose=1)

    # Plot grafik akurasi
    plt.plot(hist.history['accuracy'])
    plt.title('Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train'], loc='upper left')
    plt.show()

    # Plot grafik loss
    plt.plot(hist.history['loss'])
    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train'], loc='upper left')
    plt.show()

    model.save('chatbot_model.h5', hist)

    # Rata-rata akurasi
    avg_accuracy = numpy.mean(hist.history['accuracy'])
    print("Rata-rata akurasi: ", avg_accuracy)

    # Rata-rata loss
    avg_loss = numpy.mean(hist.history['loss'])
    print("Rata-rata loss: ", avg_loss)

    print("training done!")
# training(responsepatterns)