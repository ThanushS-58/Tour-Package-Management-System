with open('routes.py', 'r') as file:
    content = file.read()
    
# Replace all @app.route with @main_bp.route
content = content.replace('@app.route', '@main_bp.route')

# Replace app.errorhandler with main_bp.errorhandler or Blueprint.errorhandler
content = content.replace('@app.errorhandler', '@main_bp.errorhandler')

with open('routes.py', 'w') as file:
    file.write(content)
    
print("Updated all route decorators in routes.py ")
