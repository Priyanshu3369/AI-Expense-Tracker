from flask import Blueprint , request , jsonify
from werkzeug.security import generate_password_hash , check_password_hash
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.extensions import db

auth_bp = Blueprint('auth',__name__,url_prefix='/api/auth')

@auth_bp.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        name = data['name'],
        email = data['email'],
        password = hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message':'User registered successfully'}) , 201

@auth_bp.route('/login',methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password,data['password']):
        return jsonify({'error':'Invalid credentials'}) , 401
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token, 'user': {'id': user.id, 'name': user.name}})