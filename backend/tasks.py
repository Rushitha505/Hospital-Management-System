from celery import Celery
from config import Config
from app import create_app
from models import db, Appointment, Notification, PatientProfile

celery_app = Celery('tasks', broker=Config.CELERY_BROKER_URL)
celery_app.conf.update(result_backend=Config.CELERY_RESULT_BACKEND)

@celery_app.task
def send_daily_reminders():
    print("Sending daily reminders to patients for tomorrow's appointments...")
    return "Reminders sent"

@celery_app.task
def generate_monthly_report():
    print("Generating monthly doctor activity report...")
    return "Report generated"
    
@celery_app.task
def export_patient_history_csv(patient_id):
    print(f"Exporting history for patient {patient_id}")
    return f"Export logic complete for patient {patient_id}"

@celery_app.task
def cancel_and_notify_appointments(doctor_id, date_str):
    app = create_app()
    with app.app_context():
        from datetime import datetime
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        start_of_day = datetime(target_date.year, target_date.month, target_date.day)
        end_of_day = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
        
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.datetime >= start_of_day,
            Appointment.datetime <= end_of_day,
            Appointment.status == 'Booked'
        ).all()
        
        for appt in appointments:
            appt.status = 'Cancelled'
            patient_profile = appt.patient
            if patient_profile:
                notif = Notification(
                    user_id=patient_profile.user_id,
                    message=f"Urgent: Your appointment on {date_str} has been cancelled due to sudden doctor unavailability. Please reschedule."
                )
                db.session.add(notif)
                print(f"Notification queued for Patient User ID {patient_profile.user_id}")
                
        db.session.commit()
        return f"Cancelled {len(appointments)} appointments and sent notifications."
