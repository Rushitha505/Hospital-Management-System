from flask import Blueprint, request, jsonify
from models import db, User, DoctorProfile, PatientProfile, Appointment
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

admin_bp = Blueprint('admin_bp', __name__)

def admin_required():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return False
    return True

@admin_bp.route('/doctors', methods=['POST'])
@jwt_required()
def create_doctor():
    if not admin_required(): return jsonify({"msg": "Unauthorized"}), 403
    
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"msg": "Username already exists"}), 400
        
    user = User(username=data.get('username'), role='doctor')
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.commit()
    
    doctor = DoctorProfile(user_id=user.id, name=data.get('name'), specialization=data.get('specialization'))
    doctor.schedule = data.get('schedule', '{}')
    db.session.add(doctor)
    db.session.commit()
    
    return jsonify({"msg": "Doctor created successfully"}), 201

@admin_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    if not admin_required(): return jsonify({"msg": "Unauthorized"}), 403
    query_text = request.args.get('q')
    query = DoctorProfile.query
    if query_text:
        query = query.filter(
            db.or_(DoctorProfile.name.ilike(f"%{query_text}%"), DoctorProfile.specialization.ilike(f"%{query_text}%"))
        )
    doctors = query.all()
    result = []
    for d in doctors:
        user = User.query.get(d.user_id)
        result.append({
            "id": d.id,
            "user_id": d.user_id,
            "username": user.username if user else None,
            "name": d.name,
            "specialization": d.specialization,
            "schedule": d.schedule
        })
    return jsonify(result), 200

@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@jwt_required()
def delete_doctor(doctor_id):
    if not admin_required(): return jsonify({"msg": "Unauthorized"}), 403
    
    doctor = DoctorProfile.query.get_or_404(doctor_id)
    user = User.query.get(doctor.user_id)
    
    db.session.delete(doctor)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"msg": "Doctor deleted"}), 200

@admin_bp.route('/patients', methods=['GET'])
@jwt_required()
def get_patients():
    if not admin_required(): return jsonify({"msg": "Unauthorized"}), 403
    query_text = request.args.get('q')
    query = PatientProfile.query
    if query_text:
        query = query.join(User).filter(
            db.or_(PatientProfile.name.ilike(f"%{query_text}%"), User.username.ilike(f"%{query_text}%"), PatientProfile.contact.ilike(f"%{query_text}%"))
        )
    patients = query.all()
    result = []
    for p in patients:
        user = User.query.get(p.user_id)
        result.append({
            "id": p.id,
            "user_id": p.user_id,
            "username": user.username if user else None,
            "name": p.name,
            "age": p.age,
            "contact": p.contact
        })
    return jsonify(result), 200

@admin_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_all_appointments():
    if not admin_required(): return jsonify({"msg": "Unauthorized"}), 403
    appointments = Appointment.query.all()
    result = []
    for app in appointments:
        result.append({
            "id": app.id,
            "doctor_name": app.doctor.name if app.doctor else "Unknown",
            "patient_name": app.patient.name if app.patient else "Unknown",
            "datetime": app.datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "status": app.status
        })
    return jsonify(result), 200

@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@jwt_required()
def edit_doctor(doctor_id):
    if not admin_required(): return jsonify({"msg": "Unauthorized"}), 403

    doctor = DoctorProfile.query.get_or_404(doctor_id)
    data = request.get_json()
    user = User.query.get_or_404(doctor.user_id)

    if 'name' in data:
        doctor.name = data['name']
    if 'specialization' in data:
        doctor.specialization = data['specialization']
    if 'schedule' in data:
        doctor.schedule = data.get('schedule', doctor.schedule)
    if 'username' in data:
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user.id:
            return jsonify({"msg": "Username already taken."}), 400
        user.username = data['username']
    if 'password' in data and data['password']:
        user.set_password(data['password'])

    db.session.commit()
    return jsonify({"msg": "Doctor updated successfully."}), 200

@admin_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@jwt_required()
def edit_patient(patient_id):
    if not admin_required(): return jsonify({"msg": "Unauthorized"}), 403

    patient = PatientProfile.query.get_or_404(patient_id)
    data = request.get_json()
    user = User.query.get_or_404(patient.user_id)

    if 'name' in data:
        patient.name = data['name']
    if 'age' in data:
        patient.age = data['age']
    if 'contact' in data:
        patient.contact = data['contact']
    if 'username' in data:
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user.id:
            return jsonify({"msg": "Username already taken."}), 400
        user.username = data['username']
    if 'password' in data and data['password']:
        user.set_password(data['password'])

    db.session.commit()
    return jsonify({"msg": "Patient updated successfully."}), 200

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def edit_user_credentials(user_id):
    if not admin_required(): return jsonify({"msg": "Unauthorized"}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'username' in data:
        # Check if username exists on another user
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user_id:
            return jsonify({"msg": "Username already taken."}), 400
        user.username = data['username']
        
    if 'password' in data and data['password']:
        user.set_password(data['password'])
        
    db.session.commit()
    return jsonify({"msg": "User credentials updated successfully."}), 200
