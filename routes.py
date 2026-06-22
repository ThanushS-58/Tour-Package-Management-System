from flask import render_template, redirect, url_for, flash, request, jsonify, current_app, send_from_directory, Blueprint
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime, date, timedelta
import uuid

from app import db
from models import User, TourPackage, Booking, Payment, PopularDestination, SiteSettings, Feedback
from forms import BookingForm, PaymentForm, ContactForm, SpecialRequestForm, FeedbackForm
from utils import allowed_file, save_image

# Create blueprint
main_bp = Blueprint('main', __name__)

# Function to update booking status based on return date
def update_bookings_status():
    """Check and update bookings to 'Completed' if the return date has passed."""
    today = date.today()
    # Find all confirmed bookings with return dates in the past
    completed_bookings = Booking.query.filter(
        Booking.status == 'Confirmed',
        Booking.return_date < today
    ).all()

    # Update status to 'Completed'
    for booking in completed_bookings:
        booking.status = 'Completed'

    if completed_bookings:
        db.session.commit()
        print(f"Updated {len(completed_bookings)} bookings to 'Completed' status")

# Home page route
@main_bp.route('/')
def index():
    # Check for bookings that need to be marked as completed
    update_bookings_status()

    featured_packages = TourPackage.query.filter_by(is_featured=True).limit(3).all()
    if not featured_packages:
        featured_packages = TourPackage.query.limit(3).all()

    # Get popular destinations
    popular_destinations = PopularDestination.query.filter_by(is_active=True).order_by(PopularDestination.display_order).all()

    # Get background images from settings
    hero_bg = SiteSettings.query.filter_by(setting_name='home_background_hero').first()
    cta_bg = SiteSettings.query.filter_by(setting_name='home_background_cta').first()
    why_choose_bg = SiteSettings.query.filter_by(setting_name='home_background_why_choose').first()

    # Default background images if not set
    hero_background = hero_bg.setting_value if hero_bg else 'https://source.unsplash.com/1600x900/?travel,vacation'
    cta_background = cta_bg.setting_value if cta_bg else 'https://source.unsplash.com/1600x900/?tropical,paradise,beach,resort'
    why_choose_background = why_choose_bg.setting_value if why_choose_bg else 'https://source.unsplash.com/1600x900/?travel,map,compass'

    # Get testimonials for home page
    testimonials_data = db.session.query(
        Feedback, Booking, User, TourPackage
    ).join(
        Booking, Feedback.booking_id == Booking.id
    ).join(
        User, Booking.user_id == User.id
    ).join(
        TourPackage, Booking.package_id == TourPackage.id
    ).filter(
        Feedback.rating >= 4  # Only show good reviews on the homepage
    ).order_by(
        Feedback.created_at.desc()
    ).limit(3).all()

    # Prepare testimonials data
    testimonials = []
    for feedback, booking, user, package in testimonials_data:
        testimonials.append({
            'id': feedback.id,
            'rating': feedback.rating,
            'comment': feedback.comment,
            'created_at': feedback.created_at,
            'user': {
                'name': user.full_name,
                'profile_image': user.profile_image
            },
            'package_name': package.name
        })

    return render_template('index.html', 
                          featured_packages=featured_packages,
                          popular_destinations=popular_destinations,
                          hero_background=hero_background,
                          cta_background=cta_background,
                          why_choose_background=why_choose_background,
                          testimonials=testimonials)

# View all tour packages
@main_bp.route('/packages')
def packages():
    location = request.args.get('location', '')
    keyword = request.args.get('keyword', '')

    query = TourPackage.query.filter_by(is_active=True)

    if keyword:
        search = f"%{keyword}%"
        query = query.filter(
            db.or_(
                TourPackage.name.ilike(search),
                TourPackage.description.ilike(search),
                TourPackage.location.ilike(search)
            )
        )

    if location:
        query = query.filter(TourPackage.location == location)

    packages = query.all()
    return render_template('packages.html', packages=packages, selected_location=location)

# View single tour package details
@main_bp.route('/package/<int:package_id>')
def package_detail(package_id):
    package = TourPackage.query.get_or_404(package_id)

    # Fetch package reviews through bookings
    reviews = db.session.query(
        Feedback, Booking, User
    ).join(
        Booking, Feedback.booking_id == Booking.id
    ).join(
        User, Booking.user_id == User.id
    ).filter(
        Booking.package_id == package_id
    ).order_by(
        Feedback.created_at.desc()
    ).limit(5).all()

    # Prepare review data with user info
    review_data = []
    for feedback, booking, user in reviews:
        review_data.append({
            'id': feedback.id,
            'rating': feedback.rating,
            'comment': feedback.comment,
            'created_at': feedback.created_at,
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name
            }
        })

    # Calculate average rating if reviews exist
    avg_rating = 0
    if review_data:
        avg_rating = sum(review['rating'] for review in review_data) / len(review_data)

    # Get diverse package recommendations
    similar_packages = []

    # Get one package with similar location
    location_package = TourPackage.query.filter(
        TourPackage.id != package_id,
        TourPackage.location == package.location,
        TourPackage.is_active == True
    ).first()
    if location_package:
        similar_packages.append(location_package)

    # Get one package with similar price range
    price_package_filter = [
        TourPackage.id != package_id,
        TourPackage.price.between(package.price * 0.8, package.price * 1.2),
        TourPackage.is_active == True
    ]

    if location_package:
        price_package_filter.append(TourPackage.id != location_package.id)

    price_package = TourPackage.query.filter(*price_package_filter).first()
    if price_package:
        similar_packages.append(price_package)

    # Get one package with similar duration
    similar_ids = [p.id for p in similar_packages]

    # Ensure package.duration has a value (default to 1 if not set)
    duration = package.duration if package.duration is not None else 1

    duration_package = TourPackage.query.filter(
        TourPackage.id != package_id,
        ~TourPackage.id.in_(similar_ids) if similar_ids else True,
        TourPackage.duration.between(duration - 2, duration + 2),
        TourPackage.is_active == True
    ).first()
    if duration_package:
        similar_packages.append(duration_package)

    # If we still need more packages, get random ones
    if len(similar_packages) < 3:
        used_ids = [p.id for p in similar_packages]
        used_ids.append(package_id)

        remaining_packages = TourPackage.query.filter(
            ~TourPackage.id.in_(used_ids),
            TourPackage.is_active == True
        ).order_by(db.func.random()).limit(3 - len(similar_packages)).all()

        similar_packages.extend(remaining_packages)

    return render_template(
        'package_detail.html', 
        package=package, 
        similar_packages=similar_packages,
        reviews=review_data,
        avg_rating=avg_rating
    )

# Book a tour package
@main_bp.route('/booking/<int:package_id>', methods=['GET', 'POST'])
@login_required
def booking(package_id):
    package = TourPackage.query.get_or_404(package_id)
    form = BookingForm()

    # Pre-calculate return date based on travel date and package duration
    if request.method == 'GET':
        # Set default return date field based on package duration
        today = date.today()
        form.travel_date.data = today
        # Always ensure package.duration has a value (default to 1 if not set)
        duration = package.duration if package.duration is not None else 1
        form.return_date.data = today + timedelta(days=duration)

    if form.validate_on_submit():
        # Calculate return date from travel date and package duration
        # User's selected return_date will be used if provided
        travel_date = form.travel_date.data
        return_date = form.return_date.data

        # If the return date was not properly set or is before the travel date + duration
        # Ensure package.duration has a value (default to 1 if not set)
        duration = package.duration if package.duration is not None else 1
        calculated_return_date = travel_date + timedelta(days=duration)
        if return_date < calculated_return_date:
            return_date = calculated_return_date

        # Calculate total price based on number of travelers
        total_price = package.price * form.num_travelers.data

        # Create new booking
        booking = Booking(
            user_id=current_user.id,
            package_id=package.id,
            travel_date=travel_date,
            return_date=return_date,
            num_travelers=form.num_travelers.data,
            total_price=total_price,
            special_requests=form.special_requests.data,
            status='Pending'
        )

        db.session.add(booking)
        db.session.commit()

        # Redirect to payment page
        return redirect(url_for('main.payment', booking_id=booking.id))

    return render_template('booking.html', form=form, package=package)

# Payment processing
@main_bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Ensure the booking belongs to the current user
    if booking.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    form = PaymentForm()

    if form.validate_on_submit():
        try:
            try:
                # Create and immediately commit payment to ensure it's saved
                payment = Payment(
                    booking_id=booking.id,
                    amount=float(booking.total_price),
                    payment_method=form.payment_method.data,
                    transaction_id=str(uuid.uuid4())[:10],
                    status='Completed',
                    payment_date=datetime.utcnow()
                )
                db.session.add(payment)
                db.session.flush()

                # Update booking status and decrease available slots
                booking.status = 'Confirmed'
                booking.package.available_slots -= booking.num_travelers
                db.session.flush()

                # Force refresh the payment and booking objects
                db.session.refresh(payment)
                db.session.refresh(booking)

                db.session.commit()

                # Double-check payment status after commit
                payment = Payment.query.filter_by(booking_id=booking.id).first()
                if payment and payment.status != 'Completed':
                    payment.status = 'Completed'
                    db.session.commit()

            except Exception as e:
                db.session.rollback()
                raise e
        except Exception as e:
            db.session.rollback()
            flash('Error processing payment. Please try again.', 'danger')
            return redirect(url_for('main.payment', booking_id=booking.id))

        flash('Payment successful! Your booking has been confirmed.', 'success')
        return redirect(url_for('main.booking_confirmation', booking_id=booking.id))

    return render_template('payment.html', form=form, booking=booking)

# Booking confirmation
@main_bp.route('/booking/confirmation/<int:booking_id>')
@login_required
def booking_confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Ensure the booking belongs to the current user
    if booking.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    return render_template('booking_confirmation.html', booking=booking)

# User profile
@main_bp.route('/profile')
@login_required
def profile():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    return render_template('profile.html', user=current_user, bookings=bookings)

# Booking history
@main_bp.route('/booking_history')
@login_required
def booking_history():
    # Check for bookings that need to be marked as completed
    update_bookings_status()

    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    return render_template('booking_history.html', bookings=bookings)

# Cancel booking
@main_bp.route('/booking/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Ensure the booking belongs to the current user
    if booking.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    # Only pending bookings can be cancelled
    if booking.status != 'Pending':
        flash('Only pending bookings can be cancelled.', 'warning')
        return redirect(url_for('main.booking_history'))

    # Update booking status
    booking.status = 'Cancelled'

    # Update payment status if payment exists
    if booking.payment:
        booking.payment.status = 'Cancelled'

    # Free up the slots for the package
    booking.package.available_slots += booking.num_travelers

    db.session.commit()

    flash('Your journey has been cancelled successfully! The refund process will be initiated within 5-7 business days.', 'success')
    return redirect(url_for('main.booking_history'))

# Chatbot API endpoint
@main_bp.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data.get('message', '').lower()

    # Get available packages
    packages = TourPackage.query.filter_by(is_active=True).all()
    package_info = "\n".join([f"- {p.name}: {p.duration if p.duration is not None else 1} days, ${p.price}" for p in packages])

    # Dynamic chatbot responses
    if 'package' in message or 'tour' in message:
        return jsonify({'response': f"Here are our available packages:\n{package_info}"})
    elif 'payment' in message or 'upi' in message:
        return jsonify({'response': "We accept all UPI payments (GPay, PhonePe, Paytm), credit/debit cards, and bank transfers. All payment methods are secure and instant!"})
    elif 'booking' in message:
        return jsonify({'response': "You can easily book any package by clicking 'Book Now' on the package details page. We'll guide you through the payment process."})
    elif 'price' in message or 'cost' in message:
        return jsonify({'response': f"Our packages range from ${min([p.price for p in packages])} to ${max([p.price for p in packages])}. Here's the full list:\n{package_info}"})
    elif 'hello' in message or 'hi' in message:
        return jsonify({'response': "Hello! I can help you with our tour packages, bookings, and payments. What would you like to know?"})
    else:
        return jsonify({'response': "I'm here to help! You can ask me about our tour packages, prices, booking process, or payment options."})

# Error handlers
@main_bp.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
# Database viewer page
@main_bp.route('/database')
@login_required
def database_viewer():
    # Make sure user is admin
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))

    # Get all data from different tables
    users = User.query.all()
    packages = TourPackage.query.all()
    bookings = Booking.query.all()
    payments = Payment.query.all()
    destinations = PopularDestination.query.all()
    site_settings = SiteSettings.query.all()
    feedbacks = Feedback.query.all()

    return render_template('admin/database.html', 
                          users=users,
                          packages=packages,
                          bookings=bookings,
                          payments=payments,
                          destinations=destinations,
                          site_settings=site_settings,
                          feedbacks=feedbacks)

@main_bp.route('/booking/feedback/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def submit_feedback(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    if booking.status != 'Completed':
        flash('You can only provide feedback for completed bookings.', 'warning')
        return redirect(url_for('main.booking_history'))

    form = FeedbackForm()
    if form.validate_on_submit():
        # Process profile image if provided
        if form.profile_image.data:
            image_path = save_image(form.profile_image.data)
            if image_path:
                current_user.profile_image = image_path

        # Create feedback
        feedback = Feedback(
            booking_id=booking.id,
            rating=int(form.rating.data),
            comment=form.comment.data
        )

        db.session.add(feedback)
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('main.booking_history'))

    return render_template('feedback.html', form=form, booking=booking)