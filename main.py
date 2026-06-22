from app import create_app, db
from models import User

app = create_app()

# Create a built-in admin user if not exists
def create_admin_user():
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                email=+
                'admin@tourpackage.com',
                full_name='System Administrator',
                phone='1234567890',
                address='Tour Package Management Office',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists")

# Create admin user
create_admin_user()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
