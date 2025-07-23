from flask import Blueprint
from controllers.common_controller import (
    handle_search,
    view_profile,
    edit_profile
)

common_bp = Blueprint('common', __name__)

common_bp.add_url_rule('/search', 'search', handle_search)
common_bp.add_url_rule('/profile', view_func=view_profile, methods=['GET'])
common_bp.add_url_rule('/edit_profile', view_func=edit_profile, methods=['GET', 'POST'])