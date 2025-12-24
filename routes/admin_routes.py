from flask import Blueprint
from controllers import admin_controller

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Dashboard
admin_bp.route('/', methods=['GET'])(admin_controller.admin_dashboard)

# Teams - RESTful routes
admin_bp.route('/teams/new', methods=['GET'])(admin_controller.create_team)  # Show create form
admin_bp.route('/teams', methods=['POST'])(admin_controller.create_team)  # Create
admin_bp.route('/teams/<int:team_id>', methods=['GET'])(admin_controller.view_team)  # Show
admin_bp.route('/teams/<int:team_id>/edit', methods=['GET'])(admin_controller.edit_team)  # Show edit form
admin_bp.route('/teams/<int:team_id>', methods=['POST', 'PUT'])(admin_controller.edit_team)  # Update
admin_bp.route('/teams/<int:team_id>', methods=['POST', 'DELETE'])(admin_controller.delete_team)  # Delete

# Users - RESTful routes
admin_bp.route('/users', methods=['GET'])(admin_controller.view_users)  # List
admin_bp.route('/users', methods=['GET'])(admin_controller.view_users)  # List (alias for compatibility)
admin_bp.route('/users/new', methods=['GET'])(admin_controller.create_user)  # Show create form
admin_bp.route('/users', methods=['POST'])(admin_controller.create_user)  # Create
admin_bp.route('/users/<int:user_id>', methods=['GET'])(admin_controller.edit_user)  # Show user details
admin_bp.route('/users/<int:user_id>/edit', methods=['GET'])(admin_controller.edit_user)  # Show edit form
admin_bp.route('/users/<int:user_id>', methods=['POST', 'PUT'])(admin_controller.edit_user)  # Update
admin_bp.route('/users/<int:user_id>', methods=['POST', 'DELETE'])(admin_controller.delete_user)  # Delete
admin_bp.route('/users/<int:user_id>/approve', methods=['POST', 'PATCH'])(admin_controller.approve_user)  # Approve
admin_bp.route('/users/<int:user_id>/reset-password', methods=['GET', 'POST'])(admin_controller.reset_password)  # Reset password

# Reports
admin_bp.route('/reports', methods=['GET'])(admin_controller.reports)  # List
admin_bp.route('/reports/projects/<int:project_id>', methods=['GET'])(admin_controller.project_report)  # Project report

# Visitors - RESTful routes
admin_bp.route('/visitors', methods=['GET'])(admin_controller.handle_visitors)  # List
admin_bp.route('/visitors/approve', methods=['POST'])(admin_controller.approve_visitor)  # Approve
admin_bp.route('/visitors/<int:visitor_id>/suspend', methods=['PATCH'])(admin_controller.suspend_visitor)  # Suspend

# Logout
admin_bp.route('/logout', methods=['GET'])(admin_controller.logout)