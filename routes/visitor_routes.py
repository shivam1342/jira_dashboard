from flask import Blueprint
from controllers import visitor_controller

visitor_bp = Blueprint('visitor', __name__, url_prefix='/visitor')

visitor_bp.route('/projects', methods=['GET'])(visitor_controller.view_approved_projects)

visitor_bp.route('/projects/<int:project_id>', methods=['GET'])(visitor_controller.view_project_detail)

visitor_bp.route('/feedback', methods=['GET', 'POST'])(visitor_controller.submit_feedback)
