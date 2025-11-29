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

auth_bp.route('/signup', methods=['GET'])(signup_page)
auth_bp.route('/signup', methods=['POST'])(signup)

auth_bp.route('/login', methods=['GET'])(login_page)
auth_bp.route('/login', methods=['POST'])(login)
auth_bp.add_url_rule('/forgot-password', view_func=forgot_password, methods=['GET', 'POST'])
auth_bp.add_url_rule('/forgot-password/verify', view_func=verify_otp, methods=['GET', 'POST'], endpoint='verify_otp')
auth_bp.add_url_rule('/logout', view_func=logout, endpoint='logout')
