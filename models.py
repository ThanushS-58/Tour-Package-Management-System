from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200))
    profile_image = db.Column(db.String(200), default='images/avatars/placeholder.svg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<User {self.username}>'

class TourPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in days
    location = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(200))
    itinerary = db.Column(db.Text, nullable=False)
    includes = db.Column(db.Text)
    excludes = db.Column(db.Text)
    available_slots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    bookings = db.relationship('Booking', backref='package', lazy='dynamic')
    
    def __repr__(self):
        return f'<TourPackage {self.name}>'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('tour_package.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    travel_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    num_travelers = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    special_requests = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')  # Pending, Confirmed, Cancelled, Completed
    
    # Relationships
    payment = db.relationship('Payment', backref='booking', uselist=False)
    
    def __repr__(self):
        return f'<Booking {self.id}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(20), nullable=False)  # UPI, Bank Transfer, Card
    transaction_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Pending')  # Pending, Completed, Failed
    
    def __repr__(self):
        return f'<Payment {self.id}>'

class PopularDestination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slogan = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PopularDestination {self.name}>'

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add relationship to get user info through booking
    booking = db.relationship('Booking', backref='feedbacks')
    
    def __repr__(self):
        return f'<Feedback {self.id}>'

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting_name = db.Column(db.String(100), nullable=False, unique=True)
    setting_value = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<SiteSettings {self.setting_name}>'
