import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

# Configure logging jiik
logging.basicConfig(level=logging.DEBUG)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    # Create the Flask app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

    # Configure the database - use PostgreSQL from environment
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    # Fallback to SQLite if DATABASE_URL is not set (for local development)
    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        # Ensure instance directory exists for SQLite database
        instance_path = os.path.join(os.path.dirname(__file__), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        print(f"Created instance directory at {instance_path}")

        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(instance_path, "tour_package.db")
        print("Warning: Using SQLite as fallback database. Set DATABASE_URL for PostgreSQL.")

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Configure file uploads
    app.config["UPLOAD_FOLDER"] = "static/uploads"
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload size

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log in to access this page."

    with app.app_context():
        # Create upload folder if it doesn't exist
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        # Import and register blueprints
        from routes import main_bp
        from auth import auth_bp
        from admin import admin_bp
        from stripe_routes import stripe_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(stripe_bp)

        # Import models to ensure they are registered with SQLAlchemy
        from models import User, TourPackage, Booking, Payment, PopularDestination, SiteSettings

        # Create all tables
        db.create_all()

    return app

# The application instance will be created in main.py