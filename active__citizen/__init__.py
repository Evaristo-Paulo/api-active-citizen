import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets
import base64
from io import BytesIO
from PIL import Image
import imghdr
from flask_cors import CORS
from flask_login import LoginManager

BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# CONFIGUAR AUTENTICAÇÃO
app.config['SECRET_KEY'] = 'wedev.com'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASEDIR, 'reporting.db')

login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)


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


from active__citizen import routes

