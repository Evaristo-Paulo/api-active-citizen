import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time


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
    #reports = db.relationship('Report', backref='user', lazy=True)


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    #user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)


@app.route('/api/reports/add', methods=["POST"])
def add_report():
    data = request.json
    # GENERATE DATE
    str_date = data['date']
    list_date = [int(item) for item in str_date.split('-')]
    year, month, days = list_date
    datetime_date = date(year, month, days)

    # GENERATE TIME
    str_time = data['time']
    list_time = [int(item) for item in str_time.split(':')]
    hours, min = list_time
    datetime_time = time(hours, min, 0)

    if 'date' in data and 'time' in data and 'location' in data and 'description' in data:
        report = Report(date=datetime_date, time=datetime_time, location=data['location'], description=data['description'])
        db.session.add(report)
        db.session.commit()
        return jsonify({"message": "Report stored successfully"})
    return jsonify({"message": "Invalid report data"}), 400
    


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
