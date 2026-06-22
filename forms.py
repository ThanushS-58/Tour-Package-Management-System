from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField, 
    TextAreaField, FloatField, IntegerField, DateField, 
    SelectField, HiddenField, RadioField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, ValidationError, 
    NumberRange, Optional
)
from datetime import date

from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class AdminLoginForm(FlaskForm):
    username = StringField('Admin Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Admin Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=200)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken. Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered. Please use a different email address.')

class PackageForm(FlaskForm):
    name = StringField('Package Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    duration = IntegerField('Duration (days)', validators=[DataRequired(), NumberRange(min=1)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    image = FileField('Package Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'svg'], 'Images only!')])
    itinerary = TextAreaField('Itinerary', validators=[DataRequired()])
    includes = TextAreaField('Includes', validators=[Optional()])
    excludes = TextAreaField('Excludes', validators=[Optional()])
    available_slots = IntegerField('Available Slots', validators=[DataRequired(), NumberRange(min=0)])
    is_featured = BooleanField('Featured Package')
    submit = SubmitField('Submit')

class BookingForm(FlaskForm):
    travel_date = DateField('Departure Date', validators=[DataRequired()])
    return_date = DateField('Return Date', validators=[DataRequired()])
    num_travelers = IntegerField('Number of Travelers', validators=[DataRequired(), NumberRange(min=1)])
    special_requests = TextAreaField('Special Requests', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Proceed to Payment')
    
    def validate_travel_date(self, travel_date):
        if travel_date.data < date.today():
            raise ValidationError('Departure date cannot be in the past')
            
    def validate_return_date(self, return_date):
        if return_date.data < self.travel_date.data:
            raise ValidationError('Return date must be after or equal to departure date')

class PaymentForm(FlaskForm):
    payment_method = RadioField('Payment Method', 
                              choices=[('UPI', 'UPI'), 
                                       ('Bank Transfer', 'Bank Transfer'), 
                                       ('Card', 'Credit/Debit Card')],
                              validators=[DataRequired()])
    card_number = StringField('Card Number', validators=[Optional(), Length(min=16, max=16)])
    card_expiry = StringField('Expiry Date (MM/YY)', validators=[Optional()])
    card_cvv = StringField('CVV', validators=[Optional(), Length(min=3, max=3)])
    upi_id = StringField('UPI ID', validators=[Optional()])
    bank_name = StringField('Bank Name', validators=[Optional()])
    account_number = StringField('Account Number', validators=[Optional()])
    ifsc_code = StringField('IFSC Code', validators=[Optional()])
    submit = SubmitField('Complete Payment')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Send Message')

class SpecialRequestForm(FlaskForm):
    request_type = SelectField('Request Type', 
                             choices=[('Dietary', 'Dietary Restrictions'), 
                                      ('Accessibility', 'Accessibility Needs'), 
                                      ('Custom', 'Custom Itinerary'), 
                                      ('Other', 'Other')],
                             validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Submit Request')

class PopularDestinationForm(FlaskForm):
    name = StringField('Destination Name', validators=[DataRequired(), Length(max=100)])
    slogan = StringField('Slogan/Tagline', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    image = FileField('Destination Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'svg'], 'Images only!')])
    display_order = IntegerField('Display Order', validators=[Optional(), NumberRange(min=0)])
    is_active = BooleanField('Active')
    submit = SubmitField('Save Destination')

class HomeBackgroundForm(FlaskForm):
    image = FileField('Background Image', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    section = SelectField('Section', 
                        choices=[('hero', 'Hero Banner'), 
                                ('cta', 'Call to Action'), 
                                ('why_choose', 'Why Choose Us')],
                        validators=[DataRequired()])
    submit = SubmitField('Update Background')

class FeedbackForm(FlaskForm):
    rating = SelectField('Rating', 
                        choices=[(str(i), str(i)) for i in range(1, 6)],
                        validators=[DataRequired()])
    comment = TextAreaField('Your Feedback', validators=[Optional(), Length(max=500)])
    profile_image = FileField('Profile Image (optional)', 
                            validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'svg'], 'Images only!')])
    submit = SubmitField('Submit Feedback')

class PaymentApprovalForm(FlaskForm):
    status = SelectField('Payment Status', 
                      choices=[('Pending', 'Pending'), 
                               ('Completed', 'Approved'), 
                               ('Failed', 'Rejected')],
                      validators=[DataRequired()])
    notes = TextAreaField('Admin Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Payment Status')
