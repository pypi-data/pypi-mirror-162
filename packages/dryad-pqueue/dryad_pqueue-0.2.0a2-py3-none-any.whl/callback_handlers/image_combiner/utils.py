from PIL import Image, ImageDraw


def round_corners(im: Image.Image, rad: float) -> Image.Image:
    circle = Image.new("L", (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)

    alpha = Image.new("L", im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def trans_paste(
    bg_img: Image.Image, fg_iter: list[tuple[Image.Image, tuple[int, int, int, int]]]
) -> Image.Image:
    fg_img_trans = Image.new("RGBA", bg_img.size)

    for (fg, b) in fg_iter:
        fg_img_trans.paste(fg, b, mask=fg)

    new_img = Image.alpha_composite(bg_img, fg_img_trans)
    return new_img
