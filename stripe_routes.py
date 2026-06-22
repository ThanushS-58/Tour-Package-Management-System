import os
import json
from flask import Blueprint, redirect, request, flash, render_template, url_for
from flask_login import login_required, current_user
import stripe
from models import db, Booking, Payment

# Initialize Stripe with the API key from environment variables
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Create the blueprint for Stripe-related routes
stripe_bp = Blueprint('stripe', __name__, url_prefix='/stripe')

@stripe_bp.route('/create-checkout/<int:booking_id>', methods=['POST'])
@login_required
def create_checkout_session(booking_id):
    # Get the booking
    booking = Booking.query.get_or_404(booking_id)
    
    # Verify that the booking belongs to the current user
    if booking.user_id != current_user.id:
        flash('Unauthorized access to this booking', 'danger')
        return redirect(url_for('main.profile'))
    
    # Check if we already have a payment for this booking
    if booking.payment and booking.payment.status == 'Completed':
        flash('This booking has already been paid for', 'info')
        return redirect(url_for('main.booking_confirmation', booking_id=booking.id))
    
    # Domain for success and cancel URLs
    YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', '')
    
    # If REPLIT_DEV_DOMAIN isn't set, try to get from REPLIT_DOMAINS
    if not YOUR_DOMAIN and os.environ.get('REPLIT_DOMAINS'):
        YOUR_DOMAIN = os.environ.get('REPLIT_DOMAINS', '').split(',')[0]
    
    # Default to localhost if no domain is available
    if not YOUR_DOMAIN:
        YOUR_DOMAIN = "localhost:5000"
    
    try:
        # Create a Checkout Session
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Tour Package: {booking.package.name}',
                            'description': f'Booking for {booking.num_travelers} travelers on {booking.travel_date.strftime("%Y-%m-%d")}',
                        },
                        'unit_amount': int(booking.total_price * 100),  # Stripe requires amount in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f'https://{YOUR_DOMAIN}/stripe/success/{booking.id}',
            cancel_url=f'https://{YOUR_DOMAIN}/stripe/cancel/{booking.id}',
            metadata={
                'booking_id': booking.id,
                'user_id': current_user.id,
            },
        )
        
        # Create or update Payment record
        if booking.payment:
            payment = booking.payment
            payment.transaction_id = checkout_session.id
            payment.payment_method = 'Card (Stripe)'
        else:
            payment = Payment(
                booking_id=booking.id,
                amount=booking.total_price,
                payment_method='Card (Stripe)',
                transaction_id=checkout_session.id,
                status='Pending'
            )
            db.session.add(payment)
            
        db.session.commit()
        
        # Redirect to Stripe Checkout
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        flash(f'Error creating checkout session: {str(e)}', 'danger')
        return redirect(url_for('main.payment', booking_id=booking.id))

@stripe_bp.route('/success/<int:booking_id>')
@login_required
def payment_success(booking_id):
    # Get the booking
    booking = Booking.query.get_or_404(booking_id)
    
    # Update payment status
    if booking.payment:
        payment = booking.payment
        payment.status = 'Completed'
        payment.payment_date = datetime.utcnow()
        booking.status = 'Booked'
        db.session.commit()
        
    flash('Payment completed successfully!', 'success')
    return redirect(url_for('main.booking_confirmation', booking_id=booking.id))

@stripe_bp.route('/cancel/<int:booking_id>')
@login_required
def payment_cancel(booking_id):
    flash('Payment was cancelled', 'warning')
    return redirect(url_for('main.payment', booking_id=booking_id))

@stripe_bp.route('/webhook', methods=['POST'])
def webhook():
    # Webhook endpoint to receive Stripe event notifications
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    # This is a secret that should be set in your environment variables
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        # Only verify signature if we have a webhook secret
        if endpoint_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        else:
            # For development without webhook secret, parse the event data directly
            event = json.loads(payload)
    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.SignatureVerificationError as e:
        # Invalid signature
        return 'Invalid signature', 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get the booking_id from the metadata
        booking_id = session.get('metadata', {}).get('booking_id')
        
        if booking_id:
            try:
                booking_id = int(booking_id)
                booking = Booking.query.get(booking_id)
                if booking and booking.payment:
                    payment = booking.payment
                    payment.status = 'Completed'
                    booking.status = 'Confirmed'
                    db.session.commit()
            except (ValueError, TypeError):
                # Invalid booking_id
                pass
    
    return 'Success', 200