from .textbox import font
from .combiner import Config, make_image
from PIL import Image
import os

image_combiner = os.path.dirname(os.path.realpath(__file__))

title_font = font(os.path.join(image_combiner, "Roboto-Medium.ttf"), 36)
textbox_font = font(os.path.join(image_combiner, "Roboto-Light.ttf"), 36)
logo_width = 64
logo = Image.open(os.path.join(image_combiner, "logo.png")).resize(
    (logo_width, logo_width)
)


def make_image_simple(images, text):
    c = Config(
        image_w=256,
        image_h=256,
        padding_w=40,
        grid_padding=10,
        bg_color=(251, 250, 255, 0),  # fbfaff
        padding_h=20,
        corner_radius=10,
        num_rows=3,
        num_cols=3,
        textbox_height=300,
        footer_height=30,
        header_height=64,
        logo_width=logo_width,
        logo=logo,
        title_padding=8,
        footer_header_color=(32, 19, 75, 0),  # 20134B
        text_box_color=(253, 252, 254, 0),  # fdfcfe
        text_box_border=(32, 19, 75, 0),  # 20134B
        text_color=(32, 19, 75, 0),  # 20134B
        text=text,
        title_color=(251, 250, 255, 0),  # fbfaff
        title_font=title_font,
        textbox_font=textbox_font,
    )
    return make_image(c, images)
