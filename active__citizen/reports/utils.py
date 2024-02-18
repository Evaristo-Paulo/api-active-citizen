import os
import secrets
import base64
from io import BytesIO
from PIL import Image
import imghdr
from active__citizen import app


def save_picture(file):
    random_hex = secrets.token_hex(8)
    decoded_file = base64.b64decode(file)
    extension = imghdr.what(None, h=decoded_file)
    media_file = str(random_hex) + '.' + str(extension)

    starter = file.find(',')
    image_data = file[starter+1:]
    image_data = bytes(image_data, encoding="ascii")
    file_path = os.path.join(app.root_path, 'static/profile_pics', media_file)

    output_size = (125, 125)
    i = Image.open(BytesIO(base64.b64decode(image_data))).convert('RGB')
    i.thumbnail(output_size)
    i.save(file_path)

    return media_file