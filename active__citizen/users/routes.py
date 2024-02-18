from active__citizen import db
import bcrypt
from flask import request, jsonify, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
from active__citizen.models import User

users = Blueprint('users', __name__)


@users.route('/api/login', methods=["POST"])
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


@users.route('/api/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successfully"})


# USER
@users.route('/api/users/add', methods=["POST"])
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


@users.route('/api/users/show/<int:user_id>', methods=['GET'])
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


@users.route('/api/users/update/<int:user_id>', methods=["PUT"])
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
