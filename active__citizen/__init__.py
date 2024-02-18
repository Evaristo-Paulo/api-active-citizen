import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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



from active__citizen.users.routes import users
from active__citizen.reports.routes import reports
app.register_blueprint(reports)
app.register_blueprint(users)

