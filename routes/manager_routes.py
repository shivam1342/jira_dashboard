from flask import Blueprint
from controllers import manager_controller

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')

# Dashboard
manager_bp.route('/', methods=['GET'])(manager_controller.manager_dashboard)

# Projects - RESTful routes
manager_bp.route('/projects', methods=['GET'])(manager_controller.manager_dashboard)  # List (same as dashboard)
manager_bp.route('/projects', methods=['POST'])(manager_controller.create_project)  # Create project
manager_bp.route('/projects/new', methods=['GET', 'POST'])(manager_controller.create_project)  # Show create form & Create
manager_bp.route('/projects/<int:project_id>', methods=['GET'])(manager_controller.view_project_details)  # Show
manager_bp.route('/projects/<int:project_id>/edit', methods=['GET'])(manager_controller.edit_project)  # Show edit form
manager_bp.route('/projects/<int:project_id>', methods=['POST', 'PUT'])(manager_controller.edit_project)  # Update
manager_bp.route('/projects/<int:project_id>', methods=['DELETE'])(manager_controller.delete_project)  # Delete
manager_bp.route('/projects/<int:project_id>/restore', methods=['PATCH'])(manager_controller.restore_project)  # Restore
manager_bp.route('/projects/<int:project_id>/grant-access', methods=['GET', 'POST'])(manager_controller.grant_project_access)

# Tasks - RESTful routes
manager_bp.route('/projects/<int:project_id>/tasks/new', methods=['GET', 'POST'])(manager_controller.create_task)  # Show create form & Create
manager_bp.route('/tasks/<int:task_id>', methods=['GET'])(manager_controller.task_details)  # Show
manager_bp.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])(manager_controller.edit_task)  # Show edit form & Update
manager_bp.route('/tasks/<int:task_id>', methods=['PUT', 'DELETE'])(manager_controller.edit_task)  # Update/Delete
manager_bp.route('/tasks/<int:task_id>', methods=['DELETE'])(manager_controller.delete_task)  # Delete
manager_bp.route('/tasks/<int:task_id>/restore', methods=['PATCH'])(manager_controller.restore_task)  # Restore
manager_bp.route('/tasks/<int:task_id>/status', methods=['POST', 'PUT'])(manager_controller.update_task_status)  # Update status
manager_bp.route('/api/tasks/<int:task_id>/status', methods=['POST'])(manager_controller.update_task_status_api)  # API endpoint - CSRF exempt

# Subtasks - RESTful routes
manager_bp.route('/projects/<int:project_id>/subtasks/new', methods=['GET', 'POST'])(manager_controller.create_subtask)  # Show create form & Create
manager_bp.route('/subtasks/<int:subtask_id>/status', methods=['POST', 'PUT'])(manager_controller.update_subtask_status)  # Update status

# Team
manager_bp.route('/team', methods=['GET'])(manager_controller.team_details)
manager_bp.route('/team/edit', methods=['GET', 'POST', 'PUT'])(manager_controller.edit_team)

# Sprints
manager_bp.route('/projects/<int:project_id>/sprints/new', methods=['GET', 'POST'])(manager_controller.create_sprint)
manager_bp.route('/projects/<int:project_id>/assign-sprint', methods=['GET', 'POST'])(manager_controller.assign_tasks_to_sprint)
manager_bp.route('/sprints/<int:sprint_id>', methods=['GET'])(manager_controller.view_sprint_detail)
manager_bp.route('/sprints/<int:sprint_id>/edit', methods=['GET', 'POST'])(manager_controller.edit_sprint)
manager_bp.route('/tasks/<int:task_id>/remove-from-sprint', methods=['POST'])(manager_controller.remove_task_from_sprint)

# Developers
manager_bp.route('/developers/<int:developer_id>', methods=['GET'])(manager_controller.view_developer_detail)

# Logout
manager_bp.route('/logout', methods=['GET'])(manager_controller.logout)