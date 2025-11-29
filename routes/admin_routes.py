from flask import Blueprint
from controllers import admin_controller

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

admin_bp.route('/', methods=['GET'])(admin_controller.admin_dashboard)
admin_bp.route('/teams/create', methods=['GET', 'POST'])(admin_controller.create_team)
admin_bp.route('/teams/edit/<int:team_id>', methods=['GET', 'POST'])(admin_controller.edit_team)
admin_bp.route('/teams/delete/<int:team_id>', methods=['POST'])(admin_controller.delete_team)
admin_bp.route('/teams/view/<int:team_id>', methods=['GET'])(admin_controller.view_team)
admin_bp.route('/users', methods=['GET'])(admin_controller.view_users)
admin_bp.route('/users/create', methods=['GET', 'POST'])(admin_controller.create_user)
admin_bp.route('/users/approve/<int:user_id>', methods=['GET'])(admin_controller.approve_user)
admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])(admin_controller.edit_user)
admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])(admin_controller.delete_user)
admin_bp.route('/users/reset-password/<int:user_id>', methods=['GET', 'POST'])(admin_controller.reset_password)
admin_bp.route('/reports/project/<int:project_id>', methods=['GET'])(admin_controller.project_report)
admin_bp.route('/reports', methods=['GET'])(admin_controller.reports)
admin_bp.route('/visitors', methods=['GET'])(admin_controller.handle_visitors)
admin_bp.route('/visitors/approve/', methods=['POST'])(admin_controller.approve_visitor)
admin_bp.route('/visitors/suspend/<int:visitor_id>', methods=['POST'])(admin_controller.suspend_visitor)
admin_bp.route('/logout')(admin_controller.logout)