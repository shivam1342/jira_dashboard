from flask import Flask, redirect, url_for, request, render_template
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
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Load .env
load_dotenv()


app = Flask(__name__)
# Use environment variable for secret key in production
app.secret_key = os.getenv('SECRET_KEY', 'azrdfhb')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# ========================================
# LOGGING CONFIGURATION
# ========================================
def setup_logging(app):
    """Configure application logging"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Set log level based on environment
    log_level = logging.DEBUG if app.debug else logging.INFO
    
    # File handler with rotation (10MB max, keep 10 backups)
    file_handler = RotatingFileHandler(
        'logs/jiradashboard.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    
    # Log format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Add handler to app logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    
    # Log startup
    app.logger.info('='*50)
    app.logger.info('Jira Dashboard Application Starting')
    app.logger.info(f'Environment: {"Development" if app.debug else "Production"}')
    app.logger.info('='*50)

setup_logging(app)


# HTTP Method Override Middleware for RESTful routing
# Allows HTML forms to simulate PUT, PATCH, DELETE methods using _method parameter
@app.before_request
def method_override():
    if request.method == 'POST' and '_method' in request.form:
        method = request.form.get('_method').upper()
        if method in ['PUT', 'PATCH', 'DELETE']:
            request.environ['REQUEST_METHOD'] = method

# Request logging middleware
@app.before_request
def log_request():
    """Log incoming requests"""
    app.logger.info(f'{request.method} {request.path} - IP: {request.remote_addr}')


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

db.init_app(app)
migrate = Migrate(app, db)


# Comment out db.create_all() when using migrations
# Use 'flask db migrate' and 'flask db upgrade' instead
# with app.app_context():
#     db.create_all()



app.register_blueprint(common_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(manager_bp)
app.register_blueprint(developer_bp, url_prefix='/developer')
app.register_blueprint(admin_bp)
app.register_blueprint(visitor_bp)

# Exempt notification AJAX endpoints from CSRF
csrf.exempt(common_bp)


# ========================================
# ERROR HANDLERS
# ========================================

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 Forbidden errors"""
    app.logger.warning(f'403 Forbidden: {request.url} - User: {session.get("username", "Anonymous")}')
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors"""
    app.logger.warning(f'404 Not Found: {request.url}')
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors"""
    app.logger.error(f'500 Internal Server Error: {request.url}', exc_info=True)
    db.session.rollback()  # Rollback any failed database transactions
    return render_template('errors/500.html'), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions"""
    app.logger.error(f'Unhandled Exception: {str(error)}', exc_info=True)
    db.session.rollback()
    
    # Return 500 for production, detailed error for development
    if app.debug:
        raise error
    return render_template('errors/500.html'), 500



@app.route('/')
def index():
    return redirect(url_for('auth.login_page')) 

if __name__ == "__main__":
    app.run(debug=True)
