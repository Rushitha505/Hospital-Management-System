from app import create_app
from models import db, User, DoctorProfile, PatientProfile

def seed_database():
    app = create_app()
    with app.app_context():
        print("Checking for existing test accounts...")
        
        # 1. Create Sample Doctor
        if not User.query.filter_by(username='doctor1').first():
            doc_user = User(username='doctor1', role='doctor')
            doc_user.set_password('drpass123')
            db.session.add(doc_user)
            db.session.flush() # Get the new generated ID
            
            doc_profile = DoctorProfile(
                user_id=doc_user.id, 
                name='Dr. Sarah Smith', 
                specialization='Cardiology', 
                schedule='Mon-Fri 9AM-5PM'
            )
            db.session.add(doc_profile)
            print("Created sample Doctor: Dr. Sarah Smith")
        else:
            print("Doctor account already exists.")

        # 2. Create Sample Patient
        if not User.query.filter_by(username='patient1').first():
            pat_user = User(username='patient1', role='patient')
            pat_user.set_password('patpass123')
            db.session.add(pat_user)
            db.session.flush() # Get the new generated ID
            
            pat_profile = PatientProfile(
                user_id=pat_user.id, 
                name='John Doe', 
                age=35, 
                contact='555-0198'
            )
            db.session.add(pat_profile)
            print("Created sample Patient: John Doe")
        else:
            print("Patient account already exists.")

        # Save all changes unconditionally 
        db.session.commit()
        print("\n--- ✅ Database Seeding Complete ---")

if __name__ == '__main__':
    seed_database()
