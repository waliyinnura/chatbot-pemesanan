import json
import pickle
import random
from urllib.request import urlopen
import nltk
import numpy
from nltk.stem import WordNetLemmatizer
from tensorflow.python.keras.models import load_model

from patterns import responsepatterns
from train import training

lemmatizer = WordNetLemmatizer()
intents1 = json.loads(responsepatterns.text)

words = pickle.load(open("datas/words.pkl",'rb'))
classses = pickle.load(open("datas/classses.pkl",'rb'))
model = load_model("chatbot_model.h5")

def clean_up_sentence(sentence):
    sen_words = nltk.word_tokenize(sentence)
    sen_words = [lemmatizer.lemmatize(word.lower()) for word in sen_words]
    return sen_words
    
def bag_words(sentences):
    sen_words = clean_up_sentence(sentences)
    bag = [0] * len(words)
    for w in sen_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return numpy.array(bag)

def pre_class(sentence):
    bow = bag_words(sentence)
    res = model.predict(numpy.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classses[r[0]], 'probability': str(r[1])})
    return return_list

def get_answer(intents_list1, intents_json):
    # print('star')
    tag = intents_list1[0]['intent']
    print('intent list =', tag)

    for i in intents_json['intents']:
        print('tag =', i['tag'])
        if i['tag'] == tag:
            return random.choice(i['response'])   

def chat_anwser(message):
    ints = pre_class(message)
    return get_answer(ints, intents1)


def main_chat():
    print("Me : ")
    while True:
        message = input(">> ")
        if message == "stop":
            break
        res = chat_anwser(message)
        print(res)



if __name__ == '__main__':
    #training()
    main_chat()
