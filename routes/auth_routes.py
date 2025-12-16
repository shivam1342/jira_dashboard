from flask import Blueprint
from controllers.auth_controllers import (
	signup_page,
	signup,
	login_page,
	login,
	forgot_password,
	verify_otp,
	logout,
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Authentication - RESTful routes
auth_bp.route('/signup', methods=['GET'])(signup_page)  # Show signup form
auth_bp.route('/signup', methods=['POST'])(signup)  # Create account

auth_bp.route('/login', methods=['GET'])(login_page)  # Show login form
auth_bp.route('/login', methods=['POST'])(login)  # Authenticate

auth_bp.route('/password/forgot', methods=['GET', 'POST'])(forgot_password)  # Forgot password
auth_bp.route('/password/verify', methods=['GET', 'POST'])(verify_otp)  # Verify OTP

auth_bp.route('/logout', methods=['GET'])(logout)  # Logout
