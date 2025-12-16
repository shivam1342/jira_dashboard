from flask import Flask, redirect, url_for, request
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.manager_routes import manager_bp
from routes.developer_routes import developer_bp
from routes.admin_routes import admin_bp
from routes.visitor_routes import visitor_bp
from flask import session
from models import db
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from routes.common_routes import common_bp
from flask_mailman import Mail
from flask_wtf.csrf import CSRFProtect

from dotenv import load_dotenv
import os
# Load .env
load_dotenv()


app = Flask(__name__)
# Use environment variable for secret key in production
app.secret_key = os.getenv('SECRET_KEY', 'azrdfhb')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# HTTP Method Override Middleware for RESTful routing
# Allows HTML forms to simulate PUT, PATCH, DELETE methods using _method parameter
@app.before_request
def method_override():
    if request.method == 'POST' and '_method' in request.form:
        method = request.form.get('_method').upper()
        if method in ['PUT', 'PATCH', 'DELETE']:
            request.environ['REQUEST_METHOD'] = method


app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USERNAME = 'zerdragneel400@gmail.com',
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
)

mail = Mail(app)

# Initialize CSRF Protection
csrf = CSRFProtect(app)
# Exempt API endpoints that return JSON (if needed)
# csrf.exempt(some_api_blueprint)

db.init_app(app)
migrate = Migrate(app, db)


# with app.app_context():
#     db.create_all()



app.register_blueprint(common_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(manager_bp)
app.register_blueprint(developer_bp, url_prefix='/developer')
app.register_blueprint(admin_bp)
app.register_blueprint(visitor_bp)



@app.route('/')
def index():
    return redirect(url_for('auth.login_page')) 

if __name__ == "__main__":
    app.run(debug=True)
