with open('routes.py', 'r') as file:
    content = file.read()
    
# Replace url_for function calls with namespace prefixes
replacements = [
    ("url_for('index')", "url_for('main.index')"),
    ("url_for('packages')", "url_for('main.packages')"),
    ("url_for('package_detail'", "url_for('main.package_detail'"),
    ("url_for('booking'", "url_for('main.booking'"),
    ("url_for('payment'", "url_for('main.payment'"),
    ("url_for('booking_confirmation'", "url_for('main.booking_confirmation'"),
    ("url_for('profile'", "url_for('main.profile'"),
    ("url_for('booking_history'", "url_for('main.booking_history'"),
    ("url_for('cancel_booking'", "url_for('main.cancel_booking'"),
    ("url_for('submit_feedback'", "url_for('main.submit_feedback'"),
]

for old, new in replacements:
    content = content.replace(old, new)

with open('routes.py', 'w') as file:
    file.write(content)
    
print("Updated all url_for calls in routes.py")
