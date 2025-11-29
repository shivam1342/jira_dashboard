from functools import wraps
from flask import session, redirect, url_for, flash
from models.login_info import UserRole
from models.login_info import LoginInfo
from models.team_member import TeamMember, TeamRole 
from models import db

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != UserRole.admin.value:
            flash("Admin access required.", "error")
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function






def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash("You must be logged in.")
            return redirect(url_for('auth.login_page'))

        manager_membership = TeamMember.query.filter_by(user_id=user_id, role=TeamRole.manager).first()

        if not manager_membership:
            flash("Access denied. Manager access required.")
            return redirect(url_for('auth.login_page'))

        return f(*args, **kwargs)
    return decorated_function


def developer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = session.get('role')
        if not role or UserRole(role) not in [UserRole.developer, UserRole.manager]:
            flash("Access denied. developer login required.")
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function