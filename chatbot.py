import os.path
import random
import json
import pickle
import webbrowser

import numpy as np
import ssl
import curses

import requests
import psutil
import pyjokes as joke
import wolframalpha as wolf
import datetime as dt
import pyautogui as pag
import pywhatkit as kit
import wikipedia as wiki
from googlesearch import search

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.text import Text
from scrapimdb import ImdbSpider
from textblob import TextBlob
from newspaper import Article
import re
from newsapi import NewsApiClient
from PIL import Image
from bs4 import BeautifulSoup

from tensorflow.keras.models import load_model

lemmatizer = WordNetLemmatizer()
intents = json.loads(open("intents.json").read())

words = pickle.load(open("words.pkl", "rb"))
classes = pickle.load(open("classes.pkl", "rb"))
types = pickle.load(open("types.pkl", "rb"))
model = load_model("chatbotmodel.h5")

ssl._create_default_https_context = ssl._create_unverified_context  # potential security risk, but needed here

API_KEY = "d4a8a95799bc4f3d9a34ac59cebaa456"
DEFAULT_NEWS_SOURCE = "bbc-news"
NEWS_API = NewsApiClient(API_KEY)
ARGUMENTS = ["", ""]
RELAXING_MUSIC = ["https://www.youtube.com/watch?v=5qap5aO4i9A",
                  "https://www.youtube.com/watch?v=cGYyOY4XaFs",
                  "https://www.youtube.com/watch?v=M2NcuP5mRqs",
                  ]

print(classes)
print(types)
print(words)

# TODO
"""
- Screenshot            x
- Song                  x     
- Wikipedia             x
- Cpu                   x
- Jokes                 x
- Time                  x


-------
Maybe
-------
+ Notes
+ Email
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
    sentence = re.sub(r'[^\w\s]', '', sentence)
    return sentence


def remove_stopword(sentence):
    return [w for w in sentence if w not in stop_words]


def get_date():
    day = dt.date.today().day
    month = dt.datetime.now().strftime("%B")
    year = dt.datetime.today().year
    weekday = dt.datetime.today().weekday()
    if day in [1, 21, 31]:
        return f"{weekday}, the {day}st of {month}, {year}."
    elif day in [2, 22]:
        return f"{weekday}, the {day}nd of {month}, {year}."
    elif day in [3, 23]:
        return f"{weekday}, the {day}rd of {month}, {year}."
    else:
        return f"{weekday}, the {day}th of {month}, {year}."


def internet_search(request):
    synonyms_for_internet = ['internet', 'net', 'cyberspace', 'web', 'World_Wide_Web', 'WWW', 'google']

    request = request.replace("world wide web ", "")
    request = request.replace(" world wide web", "")

    cleaned_query = [remove_punctuation(request)]
    speech_words_in_query = [word_tokenize(sentence) for sentence in cleaned_query]
    filtered_query = [remove_stopword(s) for s in speech_words_in_query]
    pos = [nltk.pos_tag(tokenized_sent) for tokenized_sent in filtered_query]

    pos = pos[0]

    new_pos = [
        i
        for i in pos
        if i[0] != "search"
           and all(
            word_here.lower() != i[0]
            for word_here in synonyms_for_internet
        )
           and i[1] != "MD"
           and i[0] != "please"
           and i[0] != "get"
    ]

    query = "".join(i[0] + " " for i in new_pos)
    search_results = [
        i for i in search(query)
    ]

    search_query = query.replace(" ", "+")

    search_link = f"https://www.google.com/search?q={search_query}"

    return_links = "\n".join(search_results)

    return return_links, search_link


def image_to_ascii_art(img_path, output_file, output_dec=False):
    img = Image.open(img_path).convert("L")

    width, height = img.size
    aspect_ratio = height / width
    new_width = 80
    new_height = aspect_ratio * new_width * 0.55
    img = img.resize((new_width, int(new_height)))

    pixels = img.getdata()

    chars = ["*", "S", "#", "&", "@", "$", "%", "*", "!", ":", "."]
    new_pixels = [chars[pixel // 25] for pixel in pixels]
    new_pixels = "".join(new_pixels)

    new_pixels_count = len(new_pixels)
    ascii_image = [
        new_pixels[index: index + new_width]
        for index in range(0, new_pixels_count, new_width)
    ]
    ascii_image = "\n".join(ascii_image)
    if output_dec:
        with open(f"{output_file}.txt", "w") as f:
            f.write(ascii_image)
    return ascii_image


def get_info(tag, request, previous=False):
    # sourcery skip: extract-duplicate-method, extract-method, split-or-ifs
    if tag in ["weather", "temperature"]:
        info = requests.get('https://ipinfo.io')
        data = info.json()
        city = data['city']
        region = data['region']
        country = data['country']
        app_id = "WE385L-EVQWJ72XK8"
        client = wolf.Client(app_id)
        result = client.query('weather forecast for' + city + ', ' + country)
        weather = next(result.results).text
        w = weather.split('\n')

        ARGUMENTS[0] = ""
        ARGUMENTS[1] = ""

        if tag == "temperature":
            return w[0]
        else:
            return w[1]

    elif tag == "screenshot":
        time_at_the_moment = dt.datetime.now()
        file_name = ".\\screenshots\\" + str(time_at_the_moment).replace(":", "-") + "-screenshot.png"
        img = pag.screenshot()
        img.save(file_name)

        ARGUMENTS[0] = "screenshot"
        ARGUMENTS[1] = f"{os.path.abspath(file_name)}"

        return

    elif tag == "song":
        cleaned_query = [remove_punctuation(request)]
        speech_words_in_query = [word_tokenize(sentence) for sentence in cleaned_query]
        filtered_query = [remove_stopword(s) for s in speech_words_in_query]
        pos = [nltk.pos_tag(tokenized_sent) for tokenized_sent in filtered_query]

        pos = pos[0]

        new_pos = [
            i for i in pos
            if i[0] != "music" and i[0] != "play" and i[0] != "song" and i[1] != "MD" and i[0] != "please"
        ]

        song_name = "".join(i[0] for i in new_pos)
        kit.playonyt(song_name)

        ARGUMENTS[0] = ""
        ARGUMENTS[1] = ""

        return

    elif tag == "wikipedia":
        try:
            # query = input("What do you what to search on wikipedia?\n")

            cleaned_query = [remove_punctuation(request)]
            speech_words_in_query = [word_tokenize(sentence) for sentence in cleaned_query]
            filtered_query = [remove_stopword(s) for s in speech_words_in_query]
            pos = [nltk.pos_tag(tokenized_sent) for tokenized_sent in filtered_query]

            pos = pos[0]

            new_pos = [
                i
                for i in pos
                if i[0] != "wiki" and i[0] != "search" and i[0] != "wikipedia" and i[1] != "MD" and i[0] != "please"
                   and i[0] != "get"
            ]

            query = "".join(i[0] for i in new_pos)
            query = query.replace(" ", "")
            results = wiki.summary(query, sentences=2)
            result_page = wiki.page(query)
            return results, result_page.url
        except wiki.exceptions.PageError:
            return ""
        finally:

            # --------------------------------
            # SEPARATION FROM WIKIPEDIA TO SEARCH
            # --------------------------------

            cleaned_query = [remove_punctuation(request)]
            speech_words_in_query = [word_tokenize(sentence) for sentence in cleaned_query]
            filtered_query = [remove_stopword(s) for s in speech_words_in_query]
            pos = [nltk.pos_tag(tokenized_sent) for tokenized_sent in filtered_query]

            pos = pos[0]

            new_pos = [
                i
                for i in pos
                if i[0] != "wiki" and i[0] != "search" and i[0] != "wikipedia" and i[1] != "MD" and i[0] != "please"
                   and i[0] != "get"
            ]

            query = "".join(i[0] + " " for i in new_pos)

            query = "".join(i[0] for i in new_pos)

            search_query = query.replace(" ", "+")

            search_link = f"https://www.google.com/search?q={search_query}"

            ARGUMENTS[0] = "wikipedia"
            ARGUMENTS[1] = search_link

    elif tag == "internet_search":
        return_links, search_link = internet_search(request)

        ARGUMENTS[0] = "internet_search"
        ARGUMENTS[1] = search_link

        return return_links, search_link

    elif tag == "review":
        synonyms_for_internet_and_review = ['internet', 'net', 'cyberspace', 'web', 'World_Wide_Web', 'WWW', 'google',
                                            "review", "imdb"]

        request = request.replace("world wide web ", "")
        request = request.replace(" world wide web", "")

        cleaned_query = [remove_punctuation(request)]
        speech_words_in_query = [word_tokenize(sentence) for sentence in cleaned_query]
        filtered_query = [remove_stopword(s) for s in speech_words_in_query]
        pos = [nltk.pos_tag(tokenized_sent) for tokenized_sent in filtered_query]

        pos = pos[0]

        new_pos = [
            i
            for i in pos
            if i[0] != "search"
               and all(
                word_here.lower() != i[0]
                for word_here in synonyms_for_internet_and_review
            )
               and i[1] != "MD"
               and i[0] != "please"
               and i[0] != "get"
        ]

        query = "".join(i[0] + " " for i in new_pos)
        imdb_review = ImdbSpider(query)

        # --------------------------------
        # SEPARATION FROM REVIEW TO SEARCH
        # --------------------------------

        query = "".join(i[0] for i in new_pos)

        search_query = query.replace(" ", "+")

        search_link = f"https://www.google.com/search?q={search_query}"

        ARGUMENTS[0] = "review"
        ARGUMENTS[1] = search_link

        return imdb_review.get_rating(), imdb_review.get_link()

    elif tag == "news":
        article = NEWS_API.get_top_headlines(sources=DEFAULT_NEWS_SOURCE)

        url = article[0]["url"]
        article = Article(url)

        article.download()
        article.parse()

        article.nlp()
        analysis = TextBlob(article.text)

        ARGUMENTS[0] = "news"
        ARGUMENTS[1] = url

        return analysis, url

    elif tag == "cpu":
        usage = str(psutil.cpu_percent())
        battery = str(psutil.sensors_battery().percent)
        plugged_in = psutil.sensors_battery().power_plugged
        plugged_in = "is" if plugged_in else "is not"

        ARGUMENTS[0] = ""
        ARGUMENTS[1] = ""

        return usage, battery, plugged_in

    elif tag == "joke":
        ARGUMENTS[0] = "joke"
        ARGUMENTS[1] = joke.get_joke()
        return joke.get_joke()

    elif tag == "time":
        ARGUMENTS[0] = "time"
        ARGUMENTS[1] = get_date()
        return str(dt.datetime.now().time())[0:5]

    elif tag == "date":
        ARGUMENTS[0] = "date"
        ARGUMENTS[1] = str(dt.datetime.now().time())[0:5]
        return get_date()

    elif tag == "note":
        date = str(dt.datetime.now()).replace(":", "-")[:-7]
        file_name = f"notes/{date}-note.txt"

        text = input("What do you want to write to your file?")

        with open(file_name, "w") as f:
            f.write(text)

        ARGUMENTS[0] = "note"
        ARGUMENTS[1] = f"notepad.exe {os.path.abspath(file_name)}"

        return os.path.abspath(file_name)

    elif previous:
        if ARGUMENTS[0] != "" and ARGUMENTS[1] != "":
            if ARGUMENTS[0] in ["note", "screenshot"]:
                os.system(ARGUMENTS[1])
                ARGUMENTS[0] = ""
                ARGUMENTS[1] = ""

            elif ARGUMENTS[0] in ["internet_search", "review", "wikipedia", "news"]:
                webbrowser.open(ARGUMENTS[1])
                ARGUMENTS[0] = ""
                ARGUMENTS[1] = ""

            elif ARGUMENTS[0] in ["time", "date"]:
                print(ARGUMENTS[1])
                ARGUMENTS[0] = ""
                ARGUMENTS[1] = ""

            elif ARGUMENTS[0] == "joke":
                print(f"{ARGUMENTS[1]}\nDo you want to hear another one?")
                ARGUMENTS[0] = "joke"
                ARGUMENTS[1] = joke.get_joke()


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
    return [
        {
            "intent": classes[r[0]],
            "probability": str(r[1]),
            "type_of_intent": types[r[0]],
        }
        for r in results
    ]


def get_response(intents_list, intents_json, question):
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
                else:
                    get_info(tag, message, previous=True)
                    result = ""
                break
    except IndexError:
        result = "I don't understand!"
    return result


print("Started...")
"""
speech = "Chess.com acquired the rights and is an official broadcast partner. On our LIVE page, you'll be able to " \
         "follow the live moves with computer analysis, live chat, and video commentary by grandmasters and special " \
         "guests. GM Fabiano Caruana is just one of the world-class commentators who will be joining the team for this " \
         "event."

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

while True:
    message = input()

    ints = predict_class(message)
    res = get_response(ints, intents, message)
    print(res)
