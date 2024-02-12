import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASEDIR, 'reporting.db')

db = SQLAlchemy(app)


class TimestampModel(db.Model):
    __abstract__ = True
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    reports = db.relationship('Report', backref='user', lazy=True)


@app.route('/')
def index():
    return '<h1>Hello World!</h1>'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
