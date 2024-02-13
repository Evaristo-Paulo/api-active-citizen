import os
import bcrypt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
import secrets
import base64
from io import BytesIO
from PIL import Image
import imghdr
from flask_cors import CORS
from flask_login import UserMixin, current_user, login_user, logout_user, LoginManager, login_required


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


class TimestampModel(db.Model):
    __abstract__ = True
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    reports = db.relationship('Report', backref='user', lazy=True)


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(80), nullable=False)
    file = db.Column(db.String, nullable=True)
    description = db.Column(db.Text, nullable=False)



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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/api/login', methods=["POST"])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    convert_password = password.encode('utf-8')

    user = User.query.filter_by(username=username).first()
    hashed_password = user.password

    if user and bcrypt.checkpw(convert_password, hashed_password):
        login_user(user)
        return jsonify({"message": "Logged in successfully"})
    return jsonify({"message": "Unauthorized. Invalid credentials"}), 401


@app.route('/api/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successfully"})


# USER
@app.route('/api/users/add', methods=["POST"])
def add_user():
    data = request.json

    if 'username' in data and 'password' in data:
        username = data['username']
        user = User.query.filter_by(username=username).first()
        # VERIFICA SE JÁ EXISTE ESTE USERNAME
        if user is not None:
            return jsonify({"message": "username has been taken"}), 400
        password = data['password']
        convert_password = password.encode('utf-8')

        salt = bcrypt.gensalt(rounds=15)
        hashed_password = bcrypt.hashpw(convert_password, salt)

        email = data.get('email', '')
        phone = data.get('phone', '')

        user = User(username=username, password=hashed_password, email=email, phone=phone)

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User stored successfully"})
    
    return jsonify({"message": "Invalid user data"}), 400


@app.route('/api/users/show/<int:user_id>', methods=['GET'])
@login_required
def get_user_details(user_id):
    logged_user_id = int(current_user.id) 

    if user_id != logged_user_id:
        logged_user_id = -1

    user = User.query.filter_by(id=logged_user_id).first()

    if user:
        return jsonify({ 
            "id": user.id,
            "username": user.username,
            "email": user.email,
        })
    return jsonify({"message": "User not found"}), 404


@app.route('/api/users/update/<int:user_id>', methods=["PUT"])
@login_required
def update_user(user_id):
    logged_user_id = int(current_user.id) 

    if user_id != logged_user_id:
        logged_user_id = -1

    user = User.query.filter_by(id=logged_user_id).first()

    if user is None:
        return jsonify({"message": "User not found"}), 404
    data = request.json

    if 'username' in data:
        username = data['username']
        has_user = User.query.filter(User.username==username, User.id != user_id).first()
        # VERIFICA SE ESTE USERNAME JÁ EXISTE
        if has_user:
            return jsonify({"message": "username has been taken"}), 400
        user.username = username
    
    if 'email' in data:
        user.email = data['email']

    if 'phone' in data:
        user.phone = data['phone']

    db.session.commit()
    return jsonify({"message": "User updated successfully"})


# REPORT
@app.route('/api/reports/add', methods=["POST"])
@login_required
def add_report():
    data = request.json
    logged_user_id = int(current_user.id)

    

    if 'date' in data and 'time' in data and 'location' in data and 'description' in data:
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

        # GENERATE MEDIA FILE
        file = ''
        if 'file' in data:
            file = save_picture(data['file'])

        report = Report(user_id=logged_user_id, file=file, date=datetime_date, time=datetime_time, location=data['location'], description=data['description'])

        db.session.add(report)
        db.session.commit()

        return jsonify({"message": "Report stored successfully"})
    
    return jsonify({"message": "Invalid report data"}), 400
    

@app.route('/api/reports/delete/<int:report_id>', methods=["DELETE"])
@login_required
def delete_report(report_id):
    logged_user_id = int(current_user.id)

    report = Report.query.filter(
        Report.user_id==logged_user_id, 
        Report.id==report_id
        ).first()

    if report:
        db.session.delete(report)
        db.session.commit()

        return jsonify({"message": "Report deleted successfully"})
    
    return jsonify({"message": "Report not found"}), 404


@app.route('/api/reports/show/<int:report_id>', methods=['GET'])
def get_report_details(report_id):
    report = Report.query.get(report_id)

    if report: 
        return jsonify({ 
            "id": report.id,
            "date": report.date,
            "time": str(report.time),
            "location": report.location,
            "file": report.file,
            "description": report.description,
            "active_citizen_id": report.user_id,
            "active_citizen_name": report.user.username,
        })
    
    return jsonify({"message": "Report not found"}), 404


@app.route('/api/reports/update/<int:report_id>', methods=["PUT"])
@login_required
def update_report(report_id):
    report = Report.query.get(report_id)

    logged_user_id = int(current_user.id)

    report = Report.query.filter(
        Report.user_id==logged_user_id, 
        Report.id==report_id
        ).first()

    if report is None:
        return jsonify({"message": "Report not found"}), 404

    data = request.json

    if 'date' in data:
        # GENERATE DATE
        str_date = data['date']
        list_date = [int(item) for item in str_date.split('-')]
        year, month, days = list_date
        datetime_date = date(year, month, days)
        report.date = datetime_date
    
    if 'time' in data:
        # GENERATE TIME
        str_time = data['time']
        list_time = [int(item) for item in str_time.split(':')]
        hours, min = list_time
        datetime_time = time(hours, min, 0)
        report.time = datetime_time

    if 'location' in data:
        report.location = data['location']

    if 'description' in data:
        report.description = data['description']

    if 'file' in data:
        report.file = save_picture(data['file'])
    
    db.session.commit()
    return jsonify({"message": "Report updated successfully"})

    
@app.route('/api/reports/', methods=["GET"])
@login_required
def get_reports():
    logged_user_id = int(current_user.id)

    reports = Report.query.filter(
        Report.user_id==logged_user_id, 
        ).all()

    items = list()

    for report in reports:
        item = { 
            "id": report.id,
            "date": report.date,
            "location": report.location,
            "description": report.description,
            "active_citizen_name": report.user.username,
        }
        items.append(item)

    return jsonify({"Reports": items})
 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
