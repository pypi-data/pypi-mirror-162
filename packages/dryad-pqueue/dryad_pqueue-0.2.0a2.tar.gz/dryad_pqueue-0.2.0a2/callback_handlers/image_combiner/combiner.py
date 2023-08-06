from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass, replace
from typing import Tuple
from .utils import round_corners, trans_paste
from .textbox import text_box, ALLIGNMENT_CENTER, ALLIGNMENT_LEFT
import os
import time

Color = Tuple[int, int, int, int]


@dataclass
class Config:
    image_w: int  # Image width
    image_h: int
    padding_w: int  # Padding to the sides of the image grid
    grid_padding: int  # Padding within the image grid
    bg_color: Color  # Background color of the image
    padding_h: int  # Vertical padding between elements
    corner_radius: int  # Corner radius of images in grid
    num_rows: int  # Number of rows
    num_cols: int  # Number of columns
    # Reserved space for textbox (may use more or less) - Note: might need to change this to be dynamic?
    textbox_height: int
    header_height: int  # Header height
    footer_height: int  # Footer height
    footer_header_color: Color
    text_box_color: Color
    text_box_border: Color
    text_color: Color
    text: str
    logo: Image.Image
    logo_width: int
    title_padding: int
    title_color: Color
    title_font: ImageFont.ImageFont
    textbox_font: ImageFont.ImageFont

    def total_width(self):
        return (
            (self.num_cols * (self.image_w))
            + ((self.num_cols - 1) * self.grid_padding)  # raw images
            + ((self.padding_w * 2))  # intra-grid padding
        )  # side padding

    def total_height(self):
        return (
            (self.num_rows * (self.image_h))
            + ((self.num_cols - 1) * self.grid_padding)  # raw images
            + (self.textbox_height)  # intra-grid padding
            + (self.header_height)  # textbox reserved space
            + (self.footer_height)  # header height
            + (self.padding_h * 3)  # footer height
        )  # space between header, textbox, grid, footer

    # upper left most pixel of the grid
    # returns: left, top
    def grid_start(self):
        return (
            self.padding_w,
            self.header_height + self.textbox_height + (self.padding_h * 2),
        )

    def grid_width(self):
        return (self.image_w * self.num_cols) + (
            self.grid_padding * (self.num_cols - 1)
        )

    def grid_height(self):
        return (self.image_h * self.num_rows) + (
            self.grid_padding * (self.num_rows - 1)
        )

    def image_boxes(self) -> list[tuple[int, int, int, int]]:
        init_w, init_h = self.grid_start()

        boxes = []
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                start_w = init_w + (col * (self.image_w + self.grid_padding))
                start_h = init_h + (row * (self.image_h + self.grid_padding))
                boxes.append(
                    (start_w, start_h, start_w + self.image_w, start_h + self.image_h)
                )
        return boxes

    def textbox_box(self):
        # This is _not_ a bounding box, rather a (start, dist) box
        return (
            self.padding_w,
            self.header_height + self.padding_h,
            self.grid_width(),
            self.textbox_height,
        )

    def textbox_bbox(self):
        x, y, dx, dy = self.textbox_box()
        return (x, y, x + dx, y + dy)

    def header_bbox(self):
        return (0, 0, self.total_width(), self.header_height)

    def footer_bbox(self):
        return (
            0,
            self.total_height() - self.footer_height,
            self.total_width(),
            self.total_height(),
        )

    def logo_bbox(self):
        return (0, 0, self.logo_width, self.header_height)

    def title_box(self):
        return (
            self.logo_width + self.title_padding,
            0,
            self.total_width() - (self.logo_width + self.title_padding),
            self.header_height,
        )


def make_image(c: Config, images: list[Image.Image]) -> Image.Image:
    # Step 1: Figure out some layout details, ie: sizes

    # Resize images to a fixed width, maintaining aspect ratio
    # TODO: this assumes that if we have multiple images, they have the same aspect ratio (same height after rescaling...)
    ims = [
        im.resize((c.image_w, int(c.image_w * im.height / im.width))) for im in images
    ]

    # Round their corners
    ims = [round_corners(im, c.corner_radius) for im in ims]

    # Store -  img height
    c.image_h = ims[0].height

    canvas = Image.new("RGBA", (c.total_width(), c.total_height()), c.bg_color)

    # Dry-run of drawing textbox to see how big it is
    c.text = c.text.replace("\n", " ")
    img_draw = ImageDraw.Draw(canvas)
    bbox = text_box(
        c.text,
        img_draw,
        c.textbox_font,
        c.textbox_box(),
        ALLIGNMENT_LEFT,
        ALLIGNMENT_CENTER,
        fill=c.text_color,
        dry=True,
    )

    c.textbox_height = bbox[3] - bbox[1]

    # Step 2: Rebuild canvas with final sizes
    canvas = Image.new("RGBA", (c.total_width(), c.total_height()), c.bg_color)

    # Step 3: Paste images onto background
    # Paste images onto background
    canvas = trans_paste(canvas, zip(ims, c.image_boxes()))

    # Step 4: Prompt box
    img_draw = ImageDraw.Draw(canvas)

    # \n Might break things, remove it
    c.text = c.text.replace("\n", " ")

    # Get the size of the text
    bbox = text_box(
        c.text,
        img_draw,
        c.textbox_font,
        c.textbox_box(),
        ALLIGNMENT_LEFT,
        ALLIGNMENT_CENTER,
        fill=c.text_color,
        dry=True,
    )
    # Draw a box for it
    img_draw.rounded_rectangle(
        bbox, fill=c.text_box_color, radius=c.corner_radius, outline=c.text_box_border
    )
    # Draw the actual text
    bbox = text_box(
        c.text,
        img_draw,
        c.textbox_font,
        c.textbox_box(),
        ALLIGNMENT_LEFT,
        ALLIGNMENT_CENTER,
        fill=c.text_color,
        dry=False,
    )

    # Step 5: Header/footer
    img_draw.rectangle(c.header_bbox(), fill=c.footer_header_color)
    img_draw.rectangle(c.footer_bbox(), fill=c.footer_header_color)

    # Step 6: Logo + title
    text_box(
        "sparklpaint",
        img_draw,
        c.title_font,
        c.title_box(),
        ALLIGNMENT_LEFT,
        ALLIGNMENT_CENTER,
        fill=c.title_color,
        dry=False,
        title=True,
    )
    canvas = trans_paste(canvas, [(c.logo, c.logo_bbox())])
    canvas = round_corners(canvas, c.corner_radius)
    return canvas


if __name__ == "__main__":
    image_paths = [f"static/img/{x}" for x in os.listdir("static/img") if "jpeg" in x]

    t = time.time()
    make_image(c, "3x3.png", image_paths)
    print("Took", time.time() - t)

    c2 = replace(c)
    c2.num_cols = 2
    c2.text = "really really really really really really really really really really really really really really really long prompt"

    t = time.time()
    make_image(c2, "3x2.png", image_paths[:6])
    print("Took", time.time() - t)

    c3 = replace(c)
    c3.text = "really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really really long prompt"

    t = time.time()
    make_image(c3, "really_long.png", image_paths)
    print("Took", time.time() - t)
