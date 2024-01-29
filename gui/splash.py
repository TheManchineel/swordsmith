import PySimpleGUI as sg


def show_splash(
    message: str, time: int = 1000, font: str = ("Arial", 20), title: str = "Splash"
) -> None:
    window = sg.Window(
        title,
        layout=[
            [
                sg.Push(),
                sg.Text(message, font=font),
                sg.Push(),
            ]
        ],
        no_titlebar=True,
        finalize=True,
    )
    window.bring_to_front()
    window.read(timeout=time)
    window.close()


def get_splash(
    message: str, font: str = ("Arial", 20), title: str = "Splash"
) -> sg.Window:
    return sg.Window(
        title,
        layout=[
            [
                sg.Push(),
                sg.Text(message, font=font),
                sg.Push(),
            ]
        ],
        no_titlebar=True,
    )
