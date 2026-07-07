from flask import Blueprint, request, jsonify
from models import db, DoctorProfile, Appointment, PatientProfile, Diagnosis, DoctorAvailability
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import json
from datetime import datetime
from tasks import cancel_and_notify_appointments

doctor_bp = Blueprint('doctor_bp', __name__)

def doctor_required():
    identity = get_jwt_identity()
    claims = get_jwt()
    if claims.get('role') != 'doctor':
        return False
    return int(identity)

@doctor_bp.route('/schedule', methods=['PUT', 'GET'])
@jwt_required()
def manage_schedule():
    user_id = doctor_required()
    if not user_id: return jsonify({"msg": "Unauthorized"}), 403
    
    doctor = DoctorProfile.query.filter_by(user_id=user_id).first()
    
    if request.method == 'GET':
        return jsonify({"schedule": json.loads(doctor.schedule or '{}')}), 200
        
    data = request.get_json()
    doctor.schedule = json.dumps(data.get('schedule', {}))
    db.session.commit()
    return jsonify({"msg": "Schedule updated"}), 200

@doctor_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    user_id = doctor_required()
    if not user_id: return jsonify({"msg": "Unauthorized"}), 403
    
    doctor = DoctorProfile.query.filter_by(user_id=user_id).first()
    appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
    
    result = [{
        "id": a.id,
        "patient": a.patient.name,
        "datetime": a.datetime.isoformat(),
        "status": a.status
    } for a in appointments]
    
    return jsonify(result), 200

@doctor_bp.route('/appointments/<int:appt_id>/diagnose', methods=['POST'])
@jwt_required()
def diagnose(appt_id):
    user_id = doctor_required()
    if not user_id: return jsonify({"msg": "Unauthorized"}), 403
    
    # Must ensure appointment belongs to this doctor
    doctor = DoctorProfile.query.filter_by(user_id=user_id).first()
    appt = Appointment.query.filter_by(id=appt_id, doctor_id=doctor.id).first()
    if not appt: return jsonify({"msg": "Appointment not found"}), 404
    
    data = request.get_json()
    diag = Diagnosis.query.filter_by(appointment_id=appt.id).first()
    if diag:
        diag.details = data.get('details')
        diag.prescription = data.get('prescription')
    else:
        diag = Diagnosis(appointment_id=appt.id, details=data.get('details'), prescription=data.get('prescription'))
        db.session.add(diag)
    
    appt.status = 'Completed'
    db.session.commit()
    return jsonify({"msg": "Diagnosis saved and appointment completed"}), 200

@doctor_bp.route('/availability', methods=['GET'])
@jwt_required()
def get_availability():
    user_id = doctor_required()
    if not user_id: return jsonify({"msg": "Unauthorized"}), 403
    
    doctor = DoctorProfile.query.filter_by(user_id=user_id).first()
    availabilities = DoctorAvailability.query.filter_by(doctor_id=doctor.id).all()
    
    return jsonify([{
        "date": a.date.isoformat(),
        "is_available": a.is_available
    } for a in availabilities]), 200

@doctor_bp.route('/availability', methods=['POST'])
@jwt_required()
def set_availability():
    user_id = doctor_required()
    if not user_id: return jsonify({"msg": "Unauthorized"}), 403
    
    doctor = DoctorProfile.query.filter_by(user_id=user_id).first()
    data = request.get_json() 
    
    try:
        target_date = datetime.strptime(data['date'], "%Y-%m-%d").date()
    except Exception as e:
        return jsonify({"msg": "Invalid date format, use YYYY-MM-DD"}), 400
        
    is_available = data.get('is_available', True)
    
    avail = DoctorAvailability.query.filter_by(doctor_id=doctor.id, date=target_date).first()
    if not avail:
        avail = DoctorAvailability(doctor_id=doctor.id, date=target_date, is_available=is_available)
        db.session.add(avail)
    else:
        avail.is_available = is_available
        
    db.session.commit()
    
    if not is_available:
        # Trigger Celery to cancel and notify
        cancel_and_notify_appointments.delay(doctor.id, target_date.isoformat())
        
    return jsonify({"msg": "Availability updated"}), 200
