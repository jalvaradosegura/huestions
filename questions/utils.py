from PIL import Image, ImageFilter


def reshape_img_to_square_with_blurry_bg(img):
    if isinstance(img, str):
        path = r'{}'.format(img)  # Fix weird bug
        front_img = Image.open(path)
    else:
        front_img = Image.open(img)

    bg_output_size = (200, 200)
    bg_img = front_img.resize(bg_output_size)
    bg_img = bg_img.filter(ImageFilter.GaussianBlur(5))

    front_output_size = (200, 200)
    front_img.thumbnail(front_output_size)
    x, y = front_img.size
    size = max(200, x, y)

    bg_img.paste(front_img, (int((size - x) / 2), int((size - y) / 2)))
    return bg_img
