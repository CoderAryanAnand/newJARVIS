import datetime as dt
import wolframalpha as wolf
import pyautogui as pag
import pywhatkit as kit
import wikipedia as wiki

from googlesearch import search
from email.parser import HeaderParser
from email.utils import parseaddr
from nltk.tokenize import word_tokenize
from scrapimdb import ImdbSpider
from textblob import TextBlob
from newspaper import Article
from newsapi import NewsApiClient
from PIL import Image

import requests
import nltk
import os
import os.path
import random
import imaplib
import smtplib
import email
import psutil
import ssl

from chatbot import remove_stopword, remove_punctuation

ssl._create_default_https_context = (
    ssl._create_unverified_context
)  # potential security risk, but needed here

API_KEY = "d4a8a95799bc4f3d9a34ac59cebaa456"
DEFAULT_NEWS_SOURCE = "bbc-news"
NEWS_API = NewsApiClient(API_KEY)
ARGUMENTS = ["", ""]
RELAXING_MUSIC = [
    "https://www.youtube.com/watch?v=5qap5aO4i9A",
    "https://www.youtube.com/watch?v=cGYyOY4XaFs",
    "https://www.youtube.com/watch?v=M2NcuP5mRqs",
]
NO_ANSWER_RESPONSES = [
    "Sorry, can't understand you",
    "Please give me more info",
    "Not sure I understand",
]
APP_PASSWORD = "yrzvzurdmjrkiymn"
EMAIL_USER = "aryananand.chess@gmail.com"
IMAP_URL = "imap.gmail.com"

server = smtplib.SMTP("smtp.gmail.com", 587)
server.ehlo()
server.starttls()
server.ehlo()
server.login(EMAIL_USER, APP_PASSWORD)


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
    return f"{weekday}, the {day}th of {month}, {year}."


def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    return msg.get_payload(None, True)


def internet_search(request):
    synonyms_for_internet = [
        "internet",
        "net",
        "cyberspace",
        "web",
        "World_Wide_Web",
        "WWW",
        "google",
    ]

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
        and all(word_here.lower() != i[0] for word_here in synonyms_for_internet)
        and i[1] != "MD"
        and i[0] != "please"
        and i[0] != "get"
    ]

    query = "".join(i[0] + " " for i in new_pos)
    search_results = [i for i in search(query)]

    search_query = query.replace(" ", "+")

    search_link = f"https://www.google.com/search?q={search_query}"

    return_links = "\n".join(search_results)

    return return_links, search_link


def image_to_ascii_art(
    img_path, height_factor=0.4, new_width=80, output_file="", output_dec=False
):
    img = Image.open(img_path).convert("L")

    width, height = img.size
    aspect_ratio = height / width
    new_width = new_width
    new_height = aspect_ratio * new_width * height_factor
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


def weather_and_temperature(temperature=False):
    info = requests.get("https://ipinfo.io")
    data = info.json()
    city = data["city"]
    # region = data["region"]
    country = data["country"]
    app_id = "WE385L-EVQWJ72XK8"
    client = wolf.Client(app_id)
    result = client.query("weather forecast for" + city + ", " + country)
    weather = next(result.results).text
    w = weather.split("\n")

    if temperature:
        return w[0]
    return w[1]


def screenshot():
    time_at_the_moment = dt.datetime.now()
    file_name = (
        ".\\screenshots\\"
        + str(time_at_the_moment).replace(":", "-")
        + "-screenshot.png"
    )
    img = pag.screenshot()
    img.save(file_name)

    return file_name


def play_song(request):
    cleaned_query = [remove_punctuation(request)]
    speech_words_in_query = [word_tokenize(sentence) for sentence in cleaned_query]
    filtered_query = [remove_stopword(s) for s in speech_words_in_query]
    pos = [nltk.pos_tag(tokenized_sent) for tokenized_sent in filtered_query]

    pos = pos[0]

    new_pos = [
        i
        for i in pos
        if i[0] != "music"
        and i[0] != "play"
        and i[0] != "song"
        and i[1] != "MD"
        and i[0] != "please"
    ]

    song_name = "".join(i[0] for i in new_pos)
    song_name = song_name if song_name != "" else random.choice(RELAXING_MUSIC)
    kit.playonyt(song_name)


def search_wikipedia(request):
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
            if i[0] != "wiki"
            and i[0] != "search"
            and i[0] != "wikipedia"
            and i[1] != "MD"
            and i[0] != "please"
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

        search_wikipedia_google(request)


def search_wikipedia_google(request):
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
        if i[0] != "wiki"
        and i[0] != "search"
        and i[0] != "wikipedia"
        and i[1] != "MD"
        and i[0] != "please"
        and i[0] != "get"
    ]

    query = "".join(i[0] for i in new_pos)

    search_query = query.replace(" ", "+")

    return f"https://www.google.com/search?q={search_query}"


def review(request):
    synonyms_for_internet_and_review = [
        "internet",
        "net",
        "cyberspace",
        "web",
        "World_Wide_Web",
        "WWW",
        "google",
        "review",
        "imdb",
    ]

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
            word_here.lower() != i[0] for word_here in synonyms_for_internet_and_review
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

    return imdb_review.get_rating(), imdb_review.get_link(), search_link


def news():
    article = NEWS_API.get_top_headlines(sources=DEFAULT_NEWS_SOURCE)

    url = article[0]["url"]
    article = Article(url)

    article.download()
    article.parse()

    article.nlp()
    analysis = TextBlob(article.text)

    return analysis, url


def cpu():
    usage = str(psutil.cpu_percent())
    battery = str(psutil.sensors_battery().percent)
    plugged_in = psutil.sensors_battery().power_plugged
    plugged_in = "is" if plugged_in else "is not"

    return usage, battery, plugged_in


def note():
    date = str(dt.datetime.now()).replace(":", "-")[:-7]
    file_name = f"notes/{date}-note.txt"

    text = input("What do you want to write to your file?")

    with open(file_name, "w") as f:
        f.write(text)

    ARGUMENTS[0] = "note"
    ARGUMENTS[1] = f"notepad.exe {os.path.abspath(file_name)}"

    return os.path.abspath(file_name)


def read_email():
    con = imaplib.IMAP4_SSL(IMAP_URL)
    con.login(EMAIL_USER, APP_PASSWORD)

    con.select("Primary")

    num = con.select("Primary")
    result, data = con.fetch(num[1][0], "(RFC822)")
    raw = email.message_from_bytes(data[0][1])

    sender = parseaddr(HeaderParser().parsestr(data[0][1].decode("utf-8"))["From"])[1]

    return get_body(raw).decode("utf-8"), sender[0], sender[1]


def write_email():
    receiver = input("Receiver: ")
    subject = input("Subject: ")
    body = input("Content: ")

    msg = f"Subject: {subject}\n\n{body}"

    server.sendmail("JARVIS", receiver, msg)

    return
