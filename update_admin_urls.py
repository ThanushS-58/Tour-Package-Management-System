with open('templates/admin/base.html', 'r') as file:
    content = file.read()
    
# Replace admin URLs with blueprint prefixes
replacements = [
    ("url_for('admin_dashboard')", "url_for('admin.admin_dashboard')"),
    ("url_for('admin_packages')", "url_for('admin.admin_packages')"),
    ("url_for('add_package'", "url_for('admin.add_package'"),
    ("url_for('edit_package'", "url_for('admin.edit_package'"),
    ("url_for('admin_bookings')", "url_for('admin.admin_bookings')"),
    ("url_for('admin_users')", "url_for('admin.admin_users')"),
    ("url_for('admin_profile')", "url_for('admin.admin_profile')"),
    ("url_for('admin_logout')", "url_for('admin.admin_logout')"),
    ("request.endpoint == 'admin_dashboard'", "request.endpoint == 'admin.admin_dashboard'"),
    ("request.endpoint in ['admin_packages', 'add_package', 'edit_package']", "request.endpoint in ['admin.admin_packages', 'admin.add_package', 'admin.edit_package']"),
    ("request.endpoint == 'admin_bookings'", "request.endpoint == 'admin.admin_bookings'"),
    ("request.endpoint == 'admin_users'", "request.endpoint == 'admin.admin_users'"),
    ("request.endpoint == 'admin_profile'", "request.endpoint == 'admin.admin_profile'"),
]

for old, new in replacements:
    content = content.replace(old, new)

with open('templates/admin/base.html', 'w') as file:
    file.write(content)
    
print("Updated all admin URL references in templates/admin/base.html")
