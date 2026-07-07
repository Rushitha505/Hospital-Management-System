from flask import Blueprint, request, jsonify
from models import db, User, PatientProfile, DoctorProfile, Appointment, Diagnosis, DoctorAvailability, Notification
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
import json

patient_bp = Blueprint('patient_bp', __name__)

def patient_required():
    identity = get_jwt_identity()
    claims = get_jwt()
    if claims.get('role') != 'patient':
        return False
    return int(identity)

@patient_bp.route('/doctors', methods=['GET'])
@jwt_required()
def search_doctors():
    spec = request.args.get('specialization')
    available = request.args.get('available')

    query = DoctorProfile.query
    if spec:
        query = query.filter(DoctorProfile.specialization.ilike(f'%{spec}%'))

    doctors = query.all()
    result = []
    for d in doctors:
        try:
            schedule = json.loads(d.schedule or '{}')
        except json.JSONDecodeError:
            schedule = {}

        if available == 'true':
            next_week = []
            today = datetime.utcnow().date()
            for i in range(7):
                day = today + timedelta(days=i)
                avail = DoctorAvailability.query.filter_by(doctor_id=d.id, date=day).first()
                if avail and avail.is_available:
                    next_week.append(day.isoformat())
            if not next_week:
                continue

        result.append({"id": d.id, "name": d.name, "specialization": d.specialization, "schedule": schedule})
    return jsonify(result), 200

@patient_bp.route('/appointments', methods=['POST'])
@jwt_required()
def book_appointment():
    user_id = patient_required()
    if not user_id: return jsonify({"msg": "Unauthorized"}), 403
    
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    if not doctor_id:
        return jsonify({"msg": "Doctor ID is required."}), 400

    doctor = DoctorProfile.query.get(doctor_id)
    if not doctor:
        return jsonify({"msg": "Doctor not found."}), 404

    try:
        appt_time = datetime.fromisoformat(data.get('datetime').replace('Z', '+00:00'))
    except Exception:
        return jsonify({"msg": "Invalid datetime format. Use ISO format."}), 400
    
    target_date = appt_time.date()
    avail = DoctorAvailability.query.filter_by(doctor_id=doctor_id, date=target_date).first()
    if avail and not avail.is_available:
        return jsonify({"msg": "Doctor is not available on this date."}), 400
    
    # Check double booking
    existing = Appointment.query.filter_by(doctor_id=doctor_id, datetime=appt_time, status='Booked').first()
    if existing:
        return jsonify({"msg": "Doctor is already booked for this time."}), 400
        
    patient = PatientProfile.query.filter_by(user_id=user_id).first()
    if not patient:
        return jsonify({"msg": "Patient profile not found."}), 404
    
    appt = Appointment(doctor_id=doctor_id, patient_id=patient.id, datetime=appt_time, status='Booked')
    db.session.add(appt)
    db.session.commit()
    
    return jsonify({"msg": "Appointment booked successfully"}), 201

@patient_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
def cancel_appointment(appointment_id):
    user_id = patient_required()
    if not user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    patient = PatientProfile.query.filter_by(user_id=user_id).first()
    appointment = Appointment.query.filter_by(id=appointment_id, patient_id=patient.id).first()
    if not appointment:
        return jsonify({"msg": "Appointment not found."}), 404
    if appointment.status != 'Booked':
        return jsonify({"msg": "Only booked appointments can be cancelled."}), 400

    appointment.status = 'Cancelled'
    db.session.commit()
    return jsonify({"msg": "Appointment cancelled successfully."}), 200

@patient_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def reschedule_appointment(appointment_id):
    user_id = patient_required()
    if not user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    appointment = Appointment.query.join(PatientProfile).filter(Appointment.id == appointment_id, PatientProfile.user_id == user_id).first()
    if not appointment:
        return jsonify({"msg": "Appointment not found."}), 404
    if appointment.status != 'Booked':
        return jsonify({"msg": "Only booked appointments can be rescheduled."}), 400

    data = request.get_json()
    try:
        new_datetime = datetime.fromisoformat(data.get('datetime').replace('Z', '+00:00'))
    except Exception:
        return jsonify({"msg": "Invalid datetime format."}), 400

    if new_datetime == appointment.datetime:
        return jsonify({"msg": "No change to appointment time."}), 400

    overlap = Appointment.query.filter_by(doctor_id=appointment.doctor_id, datetime=new_datetime, status='Booked').first()
    if overlap:
        return jsonify({"msg": "Doctor is already booked for the new time."}), 400

    target_date = new_datetime.date()
    avail = DoctorAvailability.query.filter_by(doctor_id=appointment.doctor_id, date=target_date).first()
    if avail and not avail.is_available:
        return jsonify({"msg": "Doctor is not available on the new date."}), 400

    appointment.datetime = new_datetime
    db.session.commit()
    return jsonify({"msg": "Appointment rescheduled successfully."}), 200

@patient_bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    user_id = patient_required()
    if not user_id: return jsonify({"msg": "Unauthorized"}), 403
    
    patient = PatientProfile.query.filter_by(user_id=user_id).first()
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    
    result = []
    for a in appointments:
        diag = Diagnosis.query.filter_by(appointment_id=a.id).first()
        result.append({
            "id": a.id,
            "doctor": a.doctor.name,
            "datetime": a.datetime.isoformat(),
            "status": a.status,
            "diagnosis": diag.details if diag else None,
            "prescription": diag.prescription if diag else None
        })
        
    return jsonify(result), 200

@patient_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = patient_required()
    if not user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    patient = PatientProfile.query.filter_by(user_id=user_id).first()
    user = User.query.get(patient.user_id)
    data = request.get_json()

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
    return jsonify({"msg": "Profile updated successfully."}), 200

@patient_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = patient_required()
    if not user_id: return jsonify({"msg": "Unauthorized"}), 403
    
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    result = []
    for n in notifications:
        result.append({
            "id": n.id,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        })
        n.is_read = True 
    db.session.commit()
    return jsonify(result), 200

@patient_bp.route('/doctors/<int:doctor_id>/availability', methods=['GET'])
@jwt_required()
def doctor_availability(doctor_id):
    availabilities = DoctorAvailability.query.filter_by(doctor_id=doctor_id).all()
    return jsonify([{
        "date": a.date.isoformat(),
        "is_available": a.is_available
    } for a in availabilities]), 200
