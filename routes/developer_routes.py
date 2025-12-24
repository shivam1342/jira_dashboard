from flask import Blueprint
from controllers import developer_controller

developer_bp = Blueprint('developer', __name__, url_prefix='/developer')

# Dashboard
developer_bp.route('/', methods=['GET'])(developer_controller.developer_dashboard)

# Projects - RESTful routes
developer_bp.route('/projects/<int:project_id>', methods=['GET'])(developer_controller.view_project_details)

# Tasks - RESTful routes
developer_bp.route('/tasks/new', methods=['GET', 'POST'])(developer_controller.create_task)  # Show create form & Create
developer_bp.route('/tasks/<int:task_id>', methods=['GET'])(developer_controller.view_task_details)  # Show
developer_bp.route('/tasks/<int:task_id>/status', methods=['POST', 'PUT'])(developer_controller.update_task_status)  # Update status
developer_bp.route('/api/tasks/<int:task_id>/status', methods=['POST'])(developer_controller.update_task_status_api)  # API endpoint - CSRF exempt

# Subtasks - RESTful routes
developer_bp.route('/projects/<int:project_id>/subtasks/new', methods=['GET', 'POST'])(developer_controller.create_subtask)  # Show create form & Create
developer_bp.route('/subtasks/<int:subtask_id>/edit', methods=['GET', 'POST'])(developer_controller.edit_subtask)  # Edit subtask
developer_bp.route('/api/subtasks/<int:subtask_id>/status', methods=['POST'])(developer_controller.update_subtask_status_api)  # API endpoint - CSRF exempt

# Logout
developer_bp.route('/logout', methods=['GET'])(developer_controller.logout)
