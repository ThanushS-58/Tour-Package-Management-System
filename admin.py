from flask import render_template, redirect, url_for, flash, request, jsonify, Blueprint
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

from app import db
from models import User, TourPackage, Booking, Payment, PopularDestination, SiteSettings, Feedback
from forms import (
    PackageForm, AdminLoginForm, PopularDestinationForm, 
    HomeBackgroundForm, PaymentApprovalForm
)
from utils import admin_required, allowed_file, save_image

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin login
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    # Redirect if user is already logged in as admin
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))
    
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # Check if user exists, is admin, and password is correct
        if user is None or not user.is_admin or not user.check_password(form.password.data):
            flash('Invalid admin credentials', 'danger')
            return redirect(url_for('admin.login'))
        
        # Log in the admin
        login_user(user)
        
        flash('Admin login successful', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/login.html', form=form, title='Admin Login')

# Admin dashboard
@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # Get stats for dashboard
    total_packages = TourPackage.query.count()
    total_users = User.query.filter_by(is_admin=False).count()
    total_bookings = Booking.query.count()
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    
    # Calculate revenue from completed payments
    completed_payments = Payment.query.filter(
        Payment.status == 'Completed',
        Payment.payment_date.isnot(None)
    ).all()
    
    total_revenue = sum(float(payment.amount) for payment in completed_payments 
                       if payment.amount is not None and isinstance(payment.amount, (int, float)))
    
    # Get booking data for charts
    booking_data = db.session.query(
        db.func.date(Booking.booking_date).label('date'),
        db.func.count(Booking.id).label('count')
    ).group_by(db.func.date(Booking.booking_date))\
    .order_by(db.func.date(Booking.booking_date))\
    .limit(30).all()
    
    booking_dates = [str(data.date) for data in booking_data]
    booking_counts = [data.count for data in booking_data]
    
    # Get revenue data for charts
    revenue_data = db.session.query(
        db.func.date(Payment.payment_date).label('date'),
        db.func.sum(Payment.amount).label('amount')
    ).filter(Payment.status == 'Completed')\
    .group_by(db.func.date(Payment.payment_date))\
    .order_by(db.func.date(Payment.payment_date))\
    .limit(30).all()
    
    revenue_dates = [str(data.date) for data in revenue_data]
    revenue_amounts = [float(data.amount) for data in revenue_data]
    
    return render_template('admin/dashboard.html', 
                          total_packages=total_packages,
                          total_users=total_users,
                          total_bookings=total_bookings,
                          recent_bookings=recent_bookings,
                          total_revenue=total_revenue,
                          booking_dates=booking_dates,
                          booking_counts=booking_counts,
                          revenue_dates=revenue_dates,
                          revenue_amounts=revenue_amounts)

# Manage packages
@admin_bp.route('/packages')
@login_required
@admin_required
def admin_packages():
    packages = TourPackage.query.all()
    return render_template('admin/packages.html', packages=packages)

@admin_bp.route('/package/<int:package_id>')
@login_required
@admin_required
def admin_package_detail(package_id):
    package = TourPackage.query.get_or_404(package_id)
    similar_packages = TourPackage.query.filter(
        TourPackage.id != package_id,
        TourPackage.location == package.location
    ).limit(3).all()
    
    if len(similar_packages) < 3:
        price_range_packages = TourPackage.query.filter(
            TourPackage.id != package_id,
            TourPackage.location != package.location,
            TourPackage.price.between(package.price * 0.8, package.price * 1.2)
        ).limit(3 - len(similar_packages)).all()
        similar_packages.extend(price_range_packages)
    
    return render_template('admin/package_detail.html', package=package, similar_packages=similar_packages)

# Add new package
@admin_bp.route('/packages/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_package():
    form = PackageForm()
    
    if form.validate_on_submit():
        # Handle image upload
        image_path = None
        if form.image.data:
            image_path = save_image(form.image.data)
        
        # Create new package
        package = TourPackage(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            duration=form.duration.data,
            location=form.location.data,
            image_path=image_path,
            itinerary=form.itinerary.data,
            includes=form.includes.data,
            excludes=form.excludes.data,
            available_slots=form.available_slots.data,
            is_featured=form.is_featured.data,
            is_active=True
        )
        
        db.session.add(package)
        db.session.commit()
        
        flash('Package added successfully', 'success')
        return redirect(url_for('admin.admin_packages'))
    
    return render_template('admin/add_package.html', form=form, title='Add Package')

# Edit package
@admin_bp.route('/packages/edit/<int:package_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_package(package_id):
    package = TourPackage.query.get_or_404(package_id)
    form = PackageForm(obj=package)
    
    if form.validate_on_submit():
        # Update package details
        package.name = form.name.data
        package.description = form.description.data
        package.price = form.price.data
        package.duration = form.duration.data
        package.location = form.location.data
        package.itinerary = form.itinerary.data
        package.includes = form.includes.data
        package.excludes = form.excludes.data
        package.available_slots = form.available_slots.data
        package.is_featured = form.is_featured.data
        
        # Handle image upload if new image is provided
        if form.image.data:
            package.image_path = save_image(form.image.data)
        
        db.session.commit()
        
        flash('Package updated successfully', 'success')
        return redirect(url_for('admin.admin_packages'))
    
    return render_template('admin/edit_package.html', form=form, package=package, title='Edit Package')

# Delete package
@admin_bp.route('/packages/delete/<int:package_id>', methods=['POST'])
@login_required
@admin_required
def delete_package(package_id):
    package = TourPackage.query.get_or_404(package_id)
    
    # Check if package has associated bookings
    if package.bookings.count() > 0:
        # Instead of deleting, mark as inactive
        package.is_active = False
        db.session.commit()
        flash('Package has been deactivated due to existing bookings', 'warning')
    else:
        # If no bookings, delete the package
        db.session.delete(package)
        db.session.commit()
        flash('Package deleted successfully', 'success')
    
    return redirect(url_for('admin.admin_packages'))

# Manage bookings
@admin_bp.route('/bookings')
@login_required
@admin_required
def admin_bookings():
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

# Update booking status
@admin_bp.route('/bookings/update/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def update_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    
    valid_statuses = ['Pending', 'Confirmed', 'Cancelled', 'Completed']
    if new_status in valid_statuses:
        booking.status = new_status
        db.session.commit()
        flash(f'Booking status updated to {new_status}', 'success')
    else:
        flash('Invalid status', 'danger')
    
    return redirect(url_for('admin.admin_bookings'))

# Manage users
@admin_bp.route('/users')
@login_required
@admin_required
def admin_users():
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/users.html', users=users)

# Admin profile
@admin_bp.route('/profile')
@login_required
@admin_required
def admin_profile():
    return render_template('admin/profile.html', admin=current_user)

# Manage Popular Destinations
@admin_bp.route('/destinations')
@login_required
@admin_required
def admin_destinations():
    destinations = PopularDestination.query.order_by(PopularDestination.display_order).all()
    return render_template('admin/destinations.html', destinations=destinations)

# Add new destination
@admin_bp.route('/destinations/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_destination():
    form = PopularDestinationForm()
    
    if form.validate_on_submit():
        # Handle image upload
        image_path = None
        if form.image.data:
            image_path = save_image(form.image.data)
            
            if not image_path:
                flash('Invalid image format. Please upload a JPG, PNG or SVG file.', 'danger')
                return render_template('admin/add_destination.html', form=form)
        else:
            flash('Image is required for destinations.', 'danger')
            return render_template('admin/add_destination.html', form=form)
        
        # Create new destination
        destination = PopularDestination(
            name=form.name.data,
            slogan=form.slogan.data,
            description=form.description.data,
            image_path=image_path,
            display_order=form.display_order.data if form.display_order.data else 0,
            is_active=form.is_active.data
        )
        
        db.session.add(destination)
        db.session.commit()
        
        flash('Destination added successfully', 'success')
        return redirect(url_for('admin.admin_destinations'))
    
    return render_template('admin/add_destination.html', form=form, title='Add Destination')

# Edit destination
@admin_bp.route('/destinations/edit/<int:destination_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_destination(destination_id):
    destination = PopularDestination.query.get_or_404(destination_id)
    form = PopularDestinationForm(obj=destination)
    
    if form.validate_on_submit():
        # Update destination details
        destination.name = form.name.data
        destination.slogan = form.slogan.data
        destination.description = form.description.data
        destination.display_order = form.display_order.data if form.display_order.data else 0
        destination.is_active = form.is_active.data
        
        # Handle image upload if new image is provided
        if form.image.data:
            new_image_path = save_image(form.image.data)
            if new_image_path:
                destination.image_path = new_image_path
            else:
                flash('Invalid image format. Image not updated.', 'warning')
        
        db.session.commit()
        
        flash('Destination updated successfully', 'success')
        return redirect(url_for('admin.admin_destinations'))
    
    return render_template('admin/edit_destination.html', form=form, destination=destination, title='Edit Destination')

# Delete destination
@admin_bp.route('/destinations/delete/<int:destination_id>', methods=['POST'])
@login_required
@admin_required
def delete_destination(destination_id):
    destination = PopularDestination.query.get_or_404(destination_id)
    
    db.session.delete(destination)
    db.session.commit()
    
    flash('Destination deleted successfully', 'success')
    return redirect(url_for('admin.admin_destinations'))

# Manage Homepage Background
@admin_bp.route('/home-background', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_home_background():
    form = HomeBackgroundForm()
    
    if form.validate_on_submit():
        section = form.section.data
        
        # Save the image
        image_path = save_image(form.image.data)
        if not image_path:
            flash('Invalid image format.', 'danger')
            return render_template('admin/home_background.html', form=form)
        
        # Check if setting already exists
        setting_name = f"home_background_{section}"
        setting = SiteSettings.query.filter_by(setting_name=setting_name).first()
        
        if setting:
            setting.setting_value = image_path
        else:
            setting = SiteSettings(
                setting_name=setting_name,
                setting_value=image_path
            )
            db.session.add(setting)
        
        db.session.commit()
        flash('Background image updated successfully', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    # Get current backgrounds
    hero_bg = SiteSettings.query.filter_by(setting_name='home_background_hero').first()
    cta_bg = SiteSettings.query.filter_by(setting_name='home_background_cta').first()
    why_choose_bg = SiteSettings.query.filter_by(setting_name='home_background_why_choose').first()
    
    return render_template('admin/home_background.html', 
                          form=form, 
                          title='Manage Home Backgrounds',
                          hero_bg=hero_bg.setting_value if hero_bg else None,
                          cta_bg=cta_bg.setting_value if cta_bg else None,
                          why_choose_bg=why_choose_bg.setting_value if why_choose_bg else None)

# Manage Payments
@admin_bp.route('/payments')
@login_required
@admin_required
def admin_payments():
    payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    return render_template('admin/payments.html', payments=payments)

# Update payment status
@admin_bp.route('/payments/update/<int:payment_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    form = PaymentApprovalForm(obj=payment)
    
    if form.validate_on_submit():
        payment.status = form.status.data
        
        # Also update the booking status if payment is completed
        if payment.status == 'Completed':
            booking = payment.booking
            booking.status = 'Confirmed'
            flash('Booking automatically confirmed as payment was approved', 'info')
        elif payment.status == 'Failed':
            booking = payment.booking
            booking.status = 'Cancelled'
            flash('Booking automatically cancelled as payment was rejected', 'info')
        
        db.session.commit()
        flash('Payment status updated successfully', 'success')
        return redirect(url_for('admin.admin_payments'))
    
    return render_template('admin/update_payment.html', form=form, payment=payment, title='Update Payment')

# Database viewer page
@admin_bp.route('/database')
@login_required
@admin_required
def database_viewer():
    # Get all data from different tables
    users = User.query.all()
    packages = TourPackage.query.all()
    bookings = Booking.query.all()
    payments = Payment.query.all()
    destinations = PopularDestination.query.all()
    site_settings = SiteSettings.query.all()
    
    # Get feedbacks
    feedbacks = Feedback.query.all()
    
    return render_template('admin/database.html', 
                          users=users,
                          packages=packages,
                          bookings=bookings,
                          payments=payments,
                          destinations=destinations,
                          site_settings=site_settings,
                          feedbacks=feedbacks)

# Admin logout
@admin_bp.route('/logout')
@login_required
@admin_required
def admin_logout():
    # Use the same logout function but redirect to admin login
    logout_user()
    flash('Admin logged out successfully', 'success')
    return redirect(url_for('admin.admin_login'))
