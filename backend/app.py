from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db, User
from config import Config
from celery import Celery

celery_app = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)
    JWTManager(app)
    
    global celery_app
    celery_app = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery_app.conf.update(app.config)

    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.doctor import doctor_bp
    from routes.patient import patient_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')

    @app.route('/')
    def index():
        return jsonify({"message": "Hospital Management API is running"})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
