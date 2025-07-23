from flask import Blueprint
from controllers.auth_controllers import signup_page, signup, login_page, login, forgot_password, logout

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

auth_bp.route('/signup', methods=['GET'])(signup_page)
auth_bp.route('/signup', methods=['POST'])(signup)

auth_bp.route('/login', methods=['GET'])(login_page)
auth_bp.route('/login', methods=['POST'])(login)
auth_bp.add_url_rule('/auth/forgot-password', view_func=forgot_password, methods=['GET'])
auth_bp.add_url_rule('/auth/logout', view_func=logout, endpoint='logout')
