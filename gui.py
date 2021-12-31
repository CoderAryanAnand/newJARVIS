import os
import json
import webbrowser

import PySimpleGUI as sg

from pyowm import OWM
from pyowm.utils import timestamps
from simplegmail import Gmail
from github import Github
from newsapi import NewsApiClient

from chatbot import get_response, predict_class, intents

credentials = json.load(open("credentials.json"))

NAME = credentials.get("name")
LOCATION = credentials.get("location")

sg.theme("Dark")

owm = OWM(credentials.get("owm"))
mgr = owm.weather_manager()

gmail = Gmail()

g = Github(credentials.get("github"))

github_repo_data, repo_names, repo_ids, repo_urls = [[]], "", [0], ""
news_data, news_headlines, news_urls = [[]], "", ""

API_KEY = credentials.get("news")
# DEFAULT_NEWS_SOURCE = "bbc-news"
NEWS_API = NewsApiClient(API_KEY)


def get_weather(
    temp_now=False, feel=False, status=False, wind=False, humidity=False, rain=False
):
    observation = mgr.weather_at_place(LOCATION)
    w = observation.weather
    will_it_rain = mgr.forecast_at_place(LOCATION, "3h")
    today = timestamps.tomorrow()
    rain_q = will_it_rain.will_be_rainy_at(today)
    if rain_q:
        rain_tomorrow = "It is likely to rain tomorrow."
    else:
        rain_tomorrow = "It doesn't look like it will rain tomorrow."
    wind_speed = w.wind()
    temp = round(w.temperature("celsius")["temp"])
    real_feel = round(w.temperature("celsius")["feels_like"])

    if temp_now:
        return temp
    elif feel:
        return real_feel
    elif status:
        return w.status
    elif wind:
        return wind_speed["speed"]
    elif humidity:
        return w.humidity
    elif rain:
        return rain
    else:
        return


def get_emails():
    return gmail.get_primary_inbox()[:20]


messages = get_emails()

email_data = [[i.sender, i.recipient, i.subject, i.date, i.snippet] for i in messages]

tasks = ["example", "case", "instance"]


def make_window(theme, scale=None, win_size=(2560, 1440)):
    global github_repo_data, repo_names, repo_ids, repo_urls, news_data, news_urls, news_headlines
    sg.theme(theme)
    menu_def = [["&Application", ["E&xit"]], ["&Help", ["&About"]]]
    right_click_menu_def = [[], ["Exit"]]

    # Table Data
    data = [["John", 10], ["Jen", 5]]
    email_headings = ["From", "To", "Subject", "Date", "Preview"]
    github_repo_headings = ["Name", "ID", "Description", "Language", "Last Edit"]
    news_headings = ["Headline", "Author", "Source", "Date", "Description"]

    weather_frame = [
        [sg.Text(f"Current weather for {LOCATION}")],
        [
            sg.Text(
                f"{get_weather(status=True)} with winds at {get_weather(wind=True)}mph."
            )
        ],
        [
            sg.Text(
                f"Temperature: {get_weather(temp_now=True)}°C with a RealFeel of {get_weather(feel=True)}°C"
            )
        ],
        [sg.Text(f"Humidity: {get_weather(humidity=True)}%")],
    ]

    email_table = [
        sg.Table(
            values=email_data,
            headings=email_headings,
            max_col_width=20,
            background_color="black",
            auto_size_columns=True,
            def_col_width=25,
            display_row_numbers=True,
            justification="left",
            num_rows=10,
            alternating_row_color="black",
            key="-TABLE1-",
            row_height=25,
            bind_return_key=True,
            expand_x=True,
            expand_y=True,
            vertical_scroll_only=False,
            pad=5,
        )
    ]

    repo_urls = [repo.html_url for repo in g.get_user().get_repos()]
    repo_names = [repo.name for repo in g.get_user().get_repos()]
    repo_ids = [repo.id for repo in g.get_user().get_repos()]
    repo_description = [repo.description for repo in g.get_user().get_repos()]
    repo_language = [repo.language for repo in g.get_user().get_repos()]
    repo_last_edit = [repo.pushed_at for repo in g.get_user().get_repos()]

    github_repo_data = [
        [name, repo_id, desc, lang, last_ed]
        for name, repo_id, desc, lang, last_ed in zip(
            repo_names, repo_ids, repo_description, repo_language, repo_last_edit
        )
    ]

    github_repo_table = [
        sg.Table(
            values=github_repo_data,
            headings=github_repo_headings,
            max_col_width=20,
            background_color="black",
            auto_size_columns=True,
            def_col_width=25,
            display_row_numbers=True,
            justification="left",
            num_rows=10,
            alternating_row_color="black",
            key="-TABLE2-",
            row_height=25,
            bind_return_key=True,
            expand_x=True,
            expand_y=True,
            vertical_scroll_only=False,
            pad=5,
        )
    ]

    news_urls = [
        article["url"] for article in NEWS_API.get_top_headlines()["articles"][:20]
    ]
    news_headlines = [
        article["title"] for article in NEWS_API.get_top_headlines()["articles"][:20]
    ]
    news_authors = [
        article["author"] for article in NEWS_API.get_top_headlines()["articles"][:20]
    ]
    news_description = [
        article["description"]
        for article in NEWS_API.get_top_headlines()["articles"][:20]
    ]
    news_source = [
        article["source"]["name"]
        for article in NEWS_API.get_top_headlines()["articles"][:20]
    ]
    news_date = [
        article["publishedAt"]
        for article in NEWS_API.get_top_headlines()["articles"][:20]
    ]

    news_data = [
        [headline, author, source, date, desc]
        for headline, author, source, date, desc in zip(
            news_headlines, news_authors, news_source, news_date, news_description
        )
    ]

    news_table = [
        sg.Table(
            values=news_data,
            headings=news_headings,
            max_col_width=20,
            background_color="black",
            auto_size_columns=True,
            def_col_width=25,
            display_row_numbers=True,
            justification="left",
            num_rows=10,
            alternating_row_color="black",
            key="-TABLE3-",
            row_height=25,
            bind_return_key=True,
            expand_x=True,
            expand_y=True,
            vertical_scroll_only=False,
            pad=5,
        )
    ]

    email_frame = [email_table]
    github_repo_frame = [github_repo_table]
    news_frame = [news_table]

    todo_frame = [
        [
            sg.InputText("Enter ToDo Item", key="todo_item"),
            sg.Button(button_text="Add", key="add_save"),
        ],
        [sg.Listbox(values=tasks, size=(40, 10), key="items")],
        [sg.Button("Delete Task"), sg.Button("Edit")],
    ]

    general_layout = [
        [sg.Menu(menu_def, key="-MENU-")],
        [
            sg.Frame(
                "Weather",
                weather_frame,
                element_justification="l",
                title_color="darkblue",
                font="Any 16",
            )
        ],
        [
            sg.Frame(
                "Email",
                email_frame,
                title_color="darkgreen",
                font="Any 16",
                expand_x=True,
            ),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Frame(
                "Github Repositories",
                github_repo_frame,
                title_color="purple",
                font="Any 16",
                expand_x=True,
            )
        ],
        [sg.Button("Open"), sg.Button("Delete")],
        [sg.HorizontalSeparator()],
        [
            sg.Frame(
                "To Do", todo_frame, title_color="pink", font="Any 16", expand_x=True
            )
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Frame(
                "News", news_frame, title_color="green", font="Any 16", expand_x=True
            )
        ],
        [sg.HorizontalSeparator()],
        [sg.Button("Update", key="UPDATEB")],
    ]

    chat_layout = [
        [sg.Text("Talk to Jarvis!", size=21)],
        [sg.HorizontalSeparator()],
        [
            sg.Multiline(
                "", k="-MULTILINE-", expand_x=True, expand_y=True, disabled=True, enable_events=True
            )
        ],
        [
            sg.Input(
                focus=True,
                key="-CHAT_INPUT-",
                enable_events=True,
                expand_x=True,
                size=(0, 20),
            ),
            sg.Button("Enter", bind_return_key=True, size=(30, 20)),
        ],
    ]

    logging_layout = [
        [sg.Text("Anything printed will display here!")],
        [sg.Output(size=(60, 15), font="Courier 8")],
    ]

    graphing_layout = [
        [sg.Text("Anything you would use to graph will display here!")],
        [
            sg.Graph(
                (200, 200),
                (0, 0),
                (200, 200),
                background_color="black",
                key="-GRAPH-",
                enable_events=True,
            )
        ],
        [sg.T("Click anywhere on graph to draw a circle")],
        [
            sg.Table(
                values=data,
                headings=email_headings,
                max_col_width=15,
                background_color="black",
                auto_size_columns=True,
                display_row_numbers=True,
                enable_events=True,
                justification="right",
                num_rows=2,
                alternating_row_color="black",
                key="-TABLE-",
                row_height=25,
            )
        ],
    ]

    specialty_layout = [
        [sg.Text('Any "special" elements will display here!')],
        [sg.Button("Open Folder")],
        [sg.Button("Open File")],
    ]

    theme_layout = [
        [
            sg.Text(
                "See how elements look under different themes by choosing a different theme here!"
            )
        ],
        [
            sg.Listbox(
                values=sg.theme_list(),
                size=(20, 12),
                key="-THEME LISTBOX-",
                enable_events=True,
            )
        ],
        [sg.Button("Set Theme")],
    ]

    layout_column = [
        [
            sg.Column(
                general_layout,
                element_justification="center",
                key="-C-",
                scrollable=True,
            )
        ]
    ]

    layout = [
        [
            sg.Text(
                f"Welcome {NAME}",
                size=(38, 1),
                justification="center",
                font=("Helvetica", 16),
                relief=sg.RELIEF_RIDGE,
                k="-TEXT HEADING-",
                enable_events=True,
            )
        ],
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab(
                            "General", layout_column, element_justification="center"
                        ),
                        sg.Tab("Chat", chat_layout, element_justification="center"),
                    ]
                ],
                key="-TAB GROUP-",
                expand_y=True,
            )
        ],
    ]

    print(f"\n\n\n{win_size}")

    return sg.Window(
        "Your Personal Assistant",
        layout,
        element_justification="c",
        right_click_menu=right_click_menu_def,
        resizable=True,
        finalize=True,
        scaling=scale,
        size=win_size,
    )


def main():
    scale = None
    window = make_window(sg.theme(), scale)
    window.maximize()
    window.bind("<Configure>", "Configure")
    with open("email_body.html", "w") as f:
        print(f.name)

    # This is an Event Loop
    while True:
        event, values = window.read(timeout=100)
        # keep an animation running so show things are happening
        # window["-TAB GROUP-"].expand(True, False, True)
        window["-C-"].expand(True, True)
        # window["-GIF-IMAGE-"].update_animation(
        #     sg.DEFAULT_BASE64_LOADING_GIF, time_between_frames=0
        # )
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
            print("============ Event = ", event, " ==============")
            print("-------- Values Dictionary (key=value) --------")
            for key in values:
                print(key, " = ", values[key])
        if event in (None, "Exit"):
            print("[LOG] Clicked Exit!")
            break

        elif event == "About":
            print("[LOG] Clicked About!")
            sg.popup(
                "PySimpleGUI Demo All Elements",
                "Right click anywhere to see right click menu",
                "Visit each of the tabs to see available elements",
                "Output of event and values can be see in Output tab",
                "The event and values dictionary is printed after every event",
            )
        elif event == "Popup":
            print("[LOG] Clicked Popup Button!")
            sg.popup("You pressed a button!")
            print("[LOG] Dismissing Popup!")
        elif event == "Test Progress bar":
            print("[LOG] Clicked Test Progress Bar!")
            progress_bar = window["-PROGRESS BAR-"]
            for i in range(1000):
                print("[LOG] Updating progress bar by 1 step (" + str(i) + ")")
                progress_bar.UpdateBar(i + 1)
            print("[LOG] Progress bar complete!")
        elif event == "-GRAPH-":
            graph = window["-GRAPH-"]  # type: sg.Graph
            graph.draw_circle(values["-GRAPH-"], fill_color="yellow", radius=20)
            print("[LOG] Circle drawn at: " + str(values["-GRAPH-"]))
        elif event == "Open Folder":
            print("[LOG] Clicked Open Folder!")
            folder_or_file = sg.popup_get_folder("Choose your folder")
            sg.popup("You chose: " + str(folder_or_file))
            print("[LOG] User chose folder: " + str(folder_or_file))
        elif event == "Open File":
            print("[LOG] Clicked Open File!")
            folder_or_file = sg.popup_get_file("Choose your file")
            sg.popup("You chose: " + str(folder_or_file))
            print("[LOG] User chose file: " + str(folder_or_file))
        elif event == "Set Theme":
            print("[LOG] Clicked Set Theme!")
            theme_chosen = values["-THEME LISTBOX-"][0]
            print("[LOG] User Chose Theme: " + str(theme_chosen))
            window.close()
            window = make_window(theme_chosen, scale)

        elif event == "UPDATEB":
            # win_size_bef = window.size
            # scale = win_size_bef[0] / 490
            # window.scaling = scale

            window.close()
            window = make_window("Dark")  # , scale, win_size_bef

        elif event == "-TABLE1-":
            print(email_data[values["-TABLE1-"][0]])

            message_index = None

            for idx, i in enumerate(email_data):
                if i == email_data[values["-TABLE1-"][0]]:
                    message_index = idx
                    break

            with open("email_body.html", "w") as f:
                f.write(messages[message_index].html)

            webbrowser.open(f"file://{os.path.realpath('email_body.html')}")
        elif event == "-TABLE2-":
            message_index = None

            for idx, i in enumerate(repo_names):
                if i == github_repo_data[values["-TABLE2-"][0]][0]:
                    message_index = idx
                    break

            webbrowser.open(repo_urls[message_index])

        elif event == "-TABLE3-":
            message_index = None

            for idx, i in enumerate(news_headlines):
                if i == news_data[values["-TABLE3-"][0]][0]:
                    message_index = idx
                    break

            webbrowser.open(news_urls[message_index])

        elif event == "Open":
            message_index = None
            print(github_repo_data[values["-TABLE2-"][0]])
            print(github_repo_data[values["-TABLE2-"][0]][0])
            for idx, i in enumerate(repo_names):
                if i == github_repo_data[values["-TABLE2-"][0]][0]:
                    message_index = idx
                    break

            webbrowser.open(repo_urls[message_index])

        elif event == "Delete":
            message_index = None
            print(github_repo_data[values["-TABLE2-"][0]])
            print(github_repo_data[values["-TABLE2-"][0]][0])
            for idx, i in enumerate(repo_names):
                if i == github_repo_data[values["-TABLE2-"][0]][0]:
                    message_index = idx
                    break

            answer = sg.popup_yes_no(
                f"Are you sure you want to delete {repo_names[message_index]}?"
            )
            if answer == "Yes":
                for repo in g.get_user().get_repos():
                    if repo.id == repo_ids[message_index]:
                        repo.delete()
                        window.close()
                        window = make_window("Dark")
                        window.maximize()

            else:
                sg.popup_auto_close(f"Not deleting {repo_names[message_index]}")

        elif event == "add_save":
            tasks.append(values["todo_item"])
            window["items"].update(values=tasks)
            window["add_save"].update("Add")
        elif event == "Delete Task":
            tasks.remove(values["items"][0])
            window["items"].update(values=tasks)
        elif event == "Edit":
            edit_val = values["items"][0]
            try:
                tasks.remove(values["items"][0])
            except IndexError:
                print(IndexError)
            window["items"].update(values=tasks)
            window["todo_item"].update(value=edit_val)
            window["add_save"].update("Save")

        elif event == "Enter":
            msg = values["-CHAT_INPUT-"]

            if msg:
                window["-CHAT_INPUT-"].update("")
                msg1 = f"You: {msg}"
                textbox = window["-MULTILINE-"]
                textbox.update(f"{textbox.get()}\n\n{msg1}")

                ints = predict_class(msg)
                msg2 = f"JARVIS: {get_response(ints, intents, msg)}"
                textbox.update(f"{textbox.get()}\n\n{msg2}\n\n")

    os.remove("email_body.html")
    window.close()
    exit(0)


if __name__ == "__main__":
    main()
