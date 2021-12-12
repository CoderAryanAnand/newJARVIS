import os.path
import logging
import json
import pickle
import re
import random
import webbrowser

import numpy as np
import ssl

# import curses
import subprocess


import pyjokes as joke
import datetime as dt

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from rich.console import Console

from tensorflow.keras.models import load_model

from chatbot_utils import get_date, image_to_ascii_art, play_song, review, read_email, note, news, cpu, internet_search
from chatbot_utils import screenshot, write_email, search_wikipedia, weather_and_temperature, relaxing_music, server

lemmatizer = WordNetLemmatizer()
intents = json.loads(open("intents.json").read())

words = pickle.load(open("models/words.pkl", "rb"))
classes = pickle.load(open("models/classes.pkl", "rb"))
types = pickle.load(open("models/types.pkl", "rb"))
model = load_model("models/chatbotmodel.h5")

ssl._create_default_https_context = ssl._create_unverified_context  # potential security risk, but needed here

ARGUMENTS = ["", ""]
NO_ANSWER_RESPONSES = ["Sorry, can't understand you", "Please give me more info", "Not sure I understand"]

console = Console()

# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

console.log(classes)
console.log(types)
console.log(words)

# TODO
"""
- Screenshot            x
- Song                  x     
- Wikipedia             x
- Cpu                   x
- Jokes                 x
- Time                  x
- News (BBC)            x
- Notes                 x
- Relaxing/Study Music  x
- Email                 x


-------
Maybe
-------
+ Calculator
+ Open Website/App  # need intents

https://autocomplete.clearbit.com/v1/companies/suggest?query=
returns json

+ News

Sample Code:
def timesofindia():
    url = "https://timesofindia.indiatimes.com/home/headlines"
    page_request = requests.get(url)
    data = page_request.content
    soup = BeautifulSoup(data,"html.parser")

    counter = 0
    for divtag in soup.find_all('div', {'class': 'headlines-list'}):
        for ultag in divtag.find_all('ul', {'class': 'clearfix'}):
            if (counter <= 10):
                for litag in ultag.find_all('li'):
                    counter = counter + 1
                    print(str(counter) + " - https://timesofindia.indiatimes.com" + litag.find('a')['href'])
                    #print(str(counter) + "." + litag.text + " - https://timesofindia.indiatimes.com" + litag.find('a')['href'])

https://www.geeksforgeeks.org/fetching-top-news-using-news-api/


if __name__ == "__main__":
    timesofindia()

+ Whatsapp [see <head><title> and maybe <span>containing "unread"]

"""
stop_words = list(set(stopwords.words("english")))


def remove_punctuation(sentence):
    sentence = re.sub(r"[^\w\s]", "", sentence)
    return sentence


def remove_stopword(sentence):
    return [w for w in sentence if w not in stop_words]


def get_info(tag, request, previous=False):
    if tag in ["weather", "temperature"]:
        ARGUMENTS[0] = ""
        ARGUMENTS[1] = ""
        if tag == "temperature":
            return weather_and_temperature(True)
        return weather_and_temperature()

    if tag == "screenshot":
        file_name = screenshot()

        ARGUMENTS[0] = "screenshot"
        ARGUMENTS[1] = f"{os.path.abspath(file_name)}"

        return

    if tag == "song":
        play_song(request)

        ARGUMENTS[0] = ""
        ARGUMENTS[1] = ""

        return

    if tag == "relaxing_music":
        relaxing_music()

        ARGUMENTS[0] = ""
        ARGUMENTS[1] = ""

        return

    if tag == "wikipedia":
        results, url, search_link = search_wikipedia(request)

        ARGUMENTS[0] = "wikipedia"
        ARGUMENTS[1] = search_link

        return results, url

    if tag == "internet_search":
        return_links, search_link = internet_search(request)

        ARGUMENTS[0] = "internet_search"
        ARGUMENTS[1] = search_link

        return return_links, search_link

    if tag == "review":

        rating, link, search_link = review(request)

        ARGUMENTS[0] = "review"
        ARGUMENTS[1] = search_link

        return rating, link

    if tag == "news":
        analysis, url = news()

        ARGUMENTS[0] = "news"
        ARGUMENTS[1] = url

        return analysis, url

    if tag == "cpu":
        usage, battery, plugged_in = cpu()

        ARGUMENTS[0] = ""
        ARGUMENTS[1] = ""

        return usage, battery, plugged_in

    if tag == "joke":
        ARGUMENTS[0] = "joke"
        ARGUMENTS[1] = joke.get_joke()
        return joke.get_joke()

    if tag == "time":
        ARGUMENTS[0] = "time"
        ARGUMENTS[1] = get_date()
        return str(dt.datetime.now().time())[0:5]

    if tag == "date":
        ARGUMENTS[0] = "date"
        ARGUMENTS[1] = str(dt.datetime.now().time())[0:5]
        return get_date()

    if tag == "note":
        file_name = note()

        ARGUMENTS[0] = "note"
        ARGUMENTS[1] = f"notepad.exe {file_name}"
        return file_name

    if tag == "read_email":
        body, sender, sender1 = read_email()

        ARGUMENTS[0] = "read_email"
        ARGUMENTS[1] = sender1

        return body, sender

    if tag == "write_email":
        write_email()

        ARGUMENTS[0] = ""
        ARGUMENTS[1] = ""

        return

    if previous and ARGUMENTS[0] != "" and ARGUMENTS[1] != "":
        if ARGUMENTS[0] in ["note", "screenshot"]:
            subprocess.call(ARGUMENTS[1], shell=False)
            ARGUMENTS[0] = ""
            ARGUMENTS[1] = ""

        elif ARGUMENTS[0] in ["internet_search", "review", "wikipedia", "news"]:
            webbrowser.open(ARGUMENTS[1])
            ARGUMENTS[0] = ""
            ARGUMENTS[1] = ""

        elif ARGUMENTS[0] in ["time", "date"]:
            console.print(ARGUMENTS[1])
            ARGUMENTS[0] = ""
            ARGUMENTS[1] = ""

        elif ARGUMENTS[0] == "joke":
            console.print(f"{ARGUMENTS[1]}\nDo you want to hear another one?")
            ARGUMENTS[0] = "joke"
            ARGUMENTS[1] = joke.get_joke()

        elif ARGUMENTS[0] == "read_email":
            receiver = ARGUMENTS[1]
            subject = input("Subject: ")
            body = input("Content: ")

            msg = f"Subject: {subject}\n\n{body}"

            server.sendmail("JARVIS", receiver, msg)

            ARGUMENTS[0] = ""
            ARGUMENTS[1] = ""


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    bow = bag_of_words(sentence)
    result_of_model = model.predict(np.array([bow]))[0]
    error_threshold = 0.25
    results = [[i, r] for i, r in enumerate(result_of_model) if r > error_threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    sentence = sentence.replace(" ", "")
    if sentence != "":
        return [
            {
                "intent": classes[r[0]],
                "probability": str(r[1]),
                "type_of_intent": types[r[0]],
            }
            for r in results
        ]
    return [{
            "intent": "no_answer",
            "probability": "0.9629686",
            "type_of_intent": "n",
        }]


def get_response(intents_list, intents_json):
    try:
        tag = intents_list[0]["intent"]
        type_of_intent = intents_list[0]["type_of_intent"]
        list_of_intents = intents_json["intents"]
        for i in list_of_intents:
            if i["tag"] == tag:
                if type_of_intent == "n":
                    result = random.choice(i["responses"])
                    ARGUMENTS[0] = ""
                    ARGUMENTS[1] = ""
                elif tag != "continue_dialog":
                    info = get_info(tag, message)
                    # print(info)
                    result = random.choice(i["responses"]).format(info)
                elif ARGUMENTS[0] != "" and ARGUMENTS[1] != "":
                    get_info(tag, message, previous=True)
                    result = ""
                else:
                    result = "Ok..."
                break
            elif tag == "no_answer":
                result = random.choice(NO_ANSWER_RESPONSES)
                ARGUMENTS[0] = ""
                ARGUMENTS[1] = ""
    except IndexError:
        result = ""
        console.print("I don't understand!")
        console.print("Do you want me search this on the internet?")
        ARGUMENTS[0] = "internet_search"
        ARGUMENTS[1] = message
    return result


console.print("Started...")
"""
speech = "Chess.com acquired the rights and is an official broadcast partner. On our LIVE page, you'll be able to " \
         "follow the live moves with computer analysis, live chat, and video commentary by grandmasters and special " \
         "guests. GM Fabiano Caruana is just one of the world-class commentators who will be joining the team for 
         this event."

sentences = sent_tokenize(speech)


cleaned_sent = [remove_punctuation(sentence) for sentence in sentences]
speech_words = [word_tokenize(sentence) for sentence in cleaned_sent]


# print(f"Number of stopwords: {len(stop_words)}")
# print(f"First 30 stopwords:\n{stop_words[:30]}")


filtered = [remove_stopword(s) for s in speech_words]
word_count = len([w for words in speech_words for w in words])
word_count2 = len([w for words in filtered for w in words])
# print(f"Number of words before: {word_count}")
# print(f"Number of words after: {word_count2}")
# print(filtered)

POS = [nltk.pos_tag(tokenized_sent) for tokenized_sent in filtered]
# print(POS[:3])

speech_words2 = Text(word_tokenize(speech))
speech_words2.concordance("great")

"""
#
# def get_synonyms(word, pos):
#     for synset in wn.synsets(word, pos=pos_to_wordnet_pos(pos)):
#         for lemma in synset.lemmas():
#             yield lemma.name()
#
#
#
# def pos_to_wordnet_pos(penntag, returnNone=False):
#     morphy_tag = {'NN':wn.NOUN, 'JJ':wn.ADJ,
#                   'VB':wn.VERB, 'RB':wn.ADV}
#     try:
#         return morphy_tag[penntag[:2]]
#     except:
#         return None if returnNone else ''
#
# text = nltk.word_tokenize("I refuse to pick up the refuse")
#
# for word, tag in nltk.pos_tag(text):
#   print(f'word is {word}, POS is {tag}')
#
#   # Filter for unique synonyms not equal to word and sort.
#   unique = sorted(set(synonym for synonym in get_synonyms(word, tag) if synonym != word))
#
#   for synonym in unique:
#     print('\t', synonym)

print("\n" * 150, image_to_ascii_art("index.jpg", 0.37, 80))
console.print("\n", image_to_ascii_art("index.png", 0.37, 40))

while True:
    message = input("> ")

    ints = predict_class(message)
    res = get_response(ints, intents)
    console.print(res)
