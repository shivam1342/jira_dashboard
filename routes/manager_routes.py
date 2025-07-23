from flask import Blueprint
from controllers import manager_controller

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')

manager_bp.route('/', methods=['GET'])(manager_controller.manager_dashboard)

manager_bp.route('/projects/create', methods=['GET', 'POST'])(manager_controller.create_project)
manager_bp.route('/projects/edit/<int:project_id>', methods=['GET', 'POST'])(manager_controller.edit_project)
manager_bp.route('/projects/delete/<int:project_id>', methods=['POST'])(manager_controller.delete_project)

manager_bp.route('/projects/restore/<int:project_id>', methods=['POST'])(manager_controller.restore_project)
manager_bp.route('/projects/<int:project_id>/grant-access', methods=['GET', 'POST'])(manager_controller.grant_project_access)

manager_bp.route('/projects/<int:project_id>/tasks/create', methods=['GET', 'POST'])(manager_controller.create_task)
manager_bp.route('/projects/<int:project_id>/subtasks/create', methods=['GET', 'POST'])(manager_controller.create_subtask)
manager_bp.route('/team/details', methods=['GET'])(manager_controller.team_details)
manager_bp.route('/tasks/<int:task_id>/details', methods=['GET'])(manager_controller.task_details)
manager_bp.route('/subtasks/<int:subtask_id>/update-status', methods=['POST'])(manager_controller.update_subtask_status)





manager_bp.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])(manager_controller.edit_task)
manager_bp.route('/tasks/delete/<int:task_id>', methods=['POST'])(manager_controller.delete_task)
manager_bp.route('/tasks/update-status/<int:task_id>', methods=['GET', 'POST'])(manager_controller.update_task_status)
manager_bp.route('/tasks/restore/<int:task_id>', methods=['POST'])(manager_controller.restore_task)

manager_bp.route('/projects/<int:project_id>/details', methods=['GET'])(manager_controller.view_project_details)

manager_bp.route('/developer/<int:developer_id>', methods=['GET'])(manager_controller.view_developer_detail)

manager_bp.route('/logout')(manager_controller.logout)