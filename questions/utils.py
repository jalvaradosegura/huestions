from io import BytesIO
import os

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import default_storage as storage
from PIL import Image, ImageFilter


def reshape_img_to_square_with_blurry_bg(img):
    if isinstance(img, str):
        path = r'{}'.format(img)  # Fix weird bug
        front_img = Image.open(path)
    else:
        front_img = Image.open(img)

    # Palette images with Transparency expressed in bytes should be converted
    # to RGBA images
    if front_img.mode == 'P':
        front_img = front_img.convert('RGBA')

    bg_output_size = (200, 200)
    bg_img = front_img.resize(bg_output_size)
    bg_img = bg_img.filter(ImageFilter.GaussianBlur(5))

    front_output_size = (200, 200)
    front_img.thumbnail(front_output_size)
    x, y = front_img.size
    size = max(200, x, y)

    bg_img.paste(front_img, (int((size - x) / 2), int((size - y) / 2)))
    return bg_img


def reshape_img_to_square_with_blurry_bg_gcp(img_path):
    img_read = storage.open(img_path, 'r')
    img = Image.open(img_read)
    extension_no_dot = os.path.splitext(img_path)[1][1:]

    if extension_no_dot == 'jpg':
        extension_no_dot = 'jpeg'

    output_size = (200, 200)
    bg_img = img.resize(output_size)
    bg_img = bg_img.filter(ImageFilter.GaussianBlur(5))

    front_output_size = (200, 200)
    img.thumbnail(front_output_size)
    x, y = img.size
    size = max(200, x, y)
    bg_img.paste(img, (int((size - x) / 2), int((size - y) / 2)))

    in_mem_file = BytesIO()
    bg_img.save(in_mem_file, format=extension_no_dot.upper())
    img_write = storage.open(img_path, 'w+')
    img_write.write(in_mem_file.getvalue())
    img_write.close()

    img_read.close()


def create_an_img_ready_for_models(img_name):
    im = Image.new(mode='RGB', size=(1, 1))  # create a new image using PIL
    im_io = BytesIO()  # a BytesIO object for saving image
    im.save(im_io, 'JPEG')  # save the image to im_io
    im_io.seek(0)  # seek to the beginning
    return InMemoryUploadedFile(
        im_io,
        None,
        img_name,
        'image/jpeg',
        len(im_io.getvalue()),
        None,
    )
