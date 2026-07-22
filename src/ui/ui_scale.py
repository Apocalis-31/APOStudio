import ctypes

screen_w = ctypes.windll.user32.GetSystemMetrics(0)

if screen_w >= 3840:
    SCALE = 1.10
elif screen_w >= 2560:
    SCALE = 1.00
else:
    SCALE = 0.88      # <- tu ne changeras que cette valeur


def px(value):
    return max(1, round(value * SCALE))


class UI:

    FONT_TITLE = px(30)
    FONT_SUBTITLE = px(18)
    FONT_SECTION = px(18)
    FONT_TEXT = px(15)
    FONT_SMALL = px(13)

    BUTTON_HEIGHT = px(45)

    PAD = px(20)
    PAD_WINDOW = px(25)