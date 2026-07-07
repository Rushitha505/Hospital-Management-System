from flask import Blueprint, request, jsonify
from models import db, User, DoctorProfile, PatientProfile
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role') # admin, doctor, patient

    user = User.query.filter_by(username=username, role=role).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role, 'username': user.username})
    return jsonify(access_token=access_token, user={'id': user.id, 'role': user.role, 'username': user.username}), 200

@auth_bp.route('/register/patient', methods=['POST'])
def register_patient():
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"msg": "Username already exists"}), 400
    
    user = User(username=data.get('username'), role='patient')
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.commit()
    
    patient = PatientProfile(user_id=user.id, name=data.get('name'), age=data.get('age'), contact=data.get('contact'))
    db.session.add(patient)
    db.session.commit()
    
    return jsonify({"msg": "Patient registered successfully"}), 201
