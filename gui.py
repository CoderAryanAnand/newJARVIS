import os
import webbrowser

import PySimpleGUI as sg

from pyowm import OWM
from pyowm.utils import timestamps
from simplegmail import Gmail

NAME = "Aryan"
LOCATION = "Wettingen"

sg.theme("Dark")

owm = OWM("4c91a9d1955812834b13222e91aac521")
mgr = owm.weather_manager()

gmail = Gmail()


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


def make_window(theme, scale=None, win_size=(2560, 1440)):
    sg.theme(theme)
    menu_def = [["&Application", ["E&xit"]], ["&Help", ["&About"]]]
    right_click_menu_def = [[], ["Exit"]]

    # Table Data
    data = [["John", 10], ["Jen", 5]]
    headings = ["From", "To", "Subject", "Date", "Preview"]

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
            headings=headings,
            max_col_width=20,
            background_color="black",
            auto_size_columns=True,
            def_col_width=25,
            display_row_numbers=True,
            justification="left",
            num_rows=len(email_data),
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

    email_frame = [email_table]

    general_layout = [
        [sg.Menu(menu_def, key="-MENU-")],
        [
            sg.Frame(
                "Weather",
                weather_frame,
                element_justification="l",
                title_color="darkblue",
                font="Any 16",
            ),
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
            sg.Slider(orientation="h", key="-SKIDER-"),
            sg.Image(
                data=sg.DEFAULT_BASE64_LOADING_GIF,
                enable_events=True,
                key="-GIF-IMAGE-",
            ),
        ],
        [sg.Checkbox("Checkbox", default=True, k="-CB-")],
        [
            sg.Radio("Radio1", "RadioDemo", default=True, size=(10, 1), k="-R1-"),
            sg.Radio("Radio2", "RadioDemo", default=True, size=(10, 1), k="-R2-"),
        ],
        [
            sg.Combo(
                values=("Combo 1", "Combo 2", "Combo 3"),
                default_value="Combo 1",
                readonly=True,
                k="-COMBO-",
            ),
            sg.OptionMenu(
                values=("Option 1", "Option 2", "Option 3"), k="-OPTION MENU-"
            ),
        ],
        [
            sg.Spin([i for i in range(1, 11)], initial_value=10, k="-SPIN-"),
            sg.Text("Spin"),
        ],
        [
            sg.Multiline(
                "Demo of a Multi-Line Text Element!\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7\nYou "
                "get the point.",
                size=(45, 5),
                k="-MLINE-",
            )
        ],
        [
            sg.Button("Button"),
            sg.Button("Popup"),
            sg.Button(image_data=sg.DEFAULT_BASE64_ICON, key="-LOGO-"),
        ],
        [sg.Button("Update", key="UPDATEB")],
    ]

    aesthetic_layout = [
        [sg.T("Anything that you would use for asthetics is in this tab!")],
        [sg.Image(data=sg.DEFAULT_BASE64_ICON, k="-IMAGE-")],
        [
            sg.ProgressBar(1000, orientation="h", size=(20, 20), key="-PROGRESS BAR-"),
            sg.Button("Test Progress bar"),
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
                headings=headings,
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
                            "General", layout_column, element_justification="right"
                        ),
                        sg.Tab("Chat", aesthetic_layout, element_justification="center"),
                    ]
                ],
                key="-TAB GROUP-",
                expand_x=True,
                expand_y=True
            )
        ]
    ]

    print(f"\n\n\n{win_size}")

    return sg.Window(
        "All Elements Demo",
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
        window['-C-'].expand(True, True)
        window["-GIF-IMAGE-"].update_animation(
            sg.DEFAULT_BASE64_LOADING_GIF, time_between_frames=0
        )
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
            win_size_bef = window.size
            scale = win_size_bef[0] / 490
            window.scaling = scale

            window.close()
            window = make_window("Dark", scale, win_size_bef)

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

    os.remove("email_body.html")
    window.close()
    exit(0)


if __name__ == "__main__":
    main()
