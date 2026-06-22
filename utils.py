import os
import uuid
from functools import wraps
from flask import flash, redirect, url_for, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Allowed file extensions for uploads
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Save uploaded image
def save_image(image_file):
    if image_file and allowed_file(image_file.filename):
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Generate unique filename
        ext = os.path.splitext(image_file.filename)[1]
        filename = secure_filename(str(uuid.uuid4()) + ext)
        filepath = os.path.join(upload_dir, filename)

        # Save the image
        image_file.save(filepath)

        # Return path relative to static folder for proper URL generation
        return 'uploads/' + filename
    return None

# Format currency
def format_currency(amount):
    return f"₹{amount:,.2f}"

# Format date for display
def format_date(date_obj):
    if date_obj:
        return date_obj.strftime('%d %b, %Y')
    return ""

# Generate booking reference number
def generate_reference_number():
    return f"BKG-{uuid.uuid4().hex[:8].upper()}"