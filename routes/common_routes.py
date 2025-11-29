from flask import Blueprint
from controllers.common_controller import (
    handle_search,
    view_profile,
    edit_profile,
    create_note,
    edit_note,
    delete_note,
    resolve_note,
    get_notifications,
    get_all_notifications,
    mark_notification_read,
    mark_all_notifications_read,
    get_notification_count
)

common_bp = Blueprint('common', __name__)

common_bp.add_url_rule('/search', 'search', handle_search)
common_bp.add_url_rule('/profile', view_func=view_profile, methods=['GET'])
common_bp.add_url_rule('/edit_profile', view_func=edit_profile, methods=['GET', 'POST'])

# Notes routes
common_bp.add_url_rule('/task/<int:task_id>/note/create', view_func=create_note, methods=['POST'], endpoint='create_note')
common_bp.add_url_rule('/note/<int:note_id>/edit', view_func=edit_note, methods=['POST'], endpoint='edit_note')
common_bp.add_url_rule('/note/<int:note_id>/delete', view_func=delete_note, methods=['POST'], endpoint='delete_note')
common_bp.add_url_rule('/note/<int:note_id>/resolve', view_func=resolve_note, methods=['POST'], endpoint='resolve_note')

# Notifications routes
common_bp.add_url_rule('/notifications', view_func=get_notifications, methods=['GET'], endpoint='notifications')
common_bp.add_url_rule('/notifications/all', view_func=get_all_notifications, methods=['GET'], endpoint='all_notifications')
common_bp.add_url_rule('/notifications/<int:notification_id>/read', view_func=mark_notification_read, methods=['POST'], endpoint='mark_notification_read')
common_bp.add_url_rule('/notifications/read-all', view_func=mark_all_notifications_read, methods=['POST'], endpoint='mark_all_read')
common_bp.add_url_rule('/notifications/count', view_func=get_notification_count, methods=['GET'], endpoint='notification_count')