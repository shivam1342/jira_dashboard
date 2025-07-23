from flask import Blueprint
from controllers import developer_controller

developer_bp = Blueprint('developer', __name__, url_prefix='/developer')

developer_bp.route('/', methods=['GET'])(developer_controller.developer_dashboard)

developer_bp.route('/projects/<int:project_id>', methods=['GET'])(developer_controller.view_project_details)

developer_bp.route('/tasks/create', methods=['GET', 'POST'])(developer_controller.create_task)

developer_bp.route('/tasks/<int:task_id>', methods=['GET'])(developer_controller.view_task_details)

developer_bp.route('/projects/<int:project_id>/create_subtask', methods=['GET', 'POST'])(developer_controller.create_subtask)

developer_bp.route('/tasks/update/<int:task_id>', methods=['GET', 'POST'])(developer_controller.update_task_status)

developer_bp.route('/api/tasks/<int:task_id>/status', methods=['POST'])(developer_controller.update_task_status_api)

developer_bp.route('/logout')(developer_controller.logout)
