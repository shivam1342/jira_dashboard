from models import db
import enum

class UserRole(enum.Enum):
    admin = 'admin'
    manager = 'manager'
    developer = 'developer'
    visitor = 'visitor'

class LoginInfo(db.Model):
    __tablename__ = 'login_info'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)

    profile = db.relationship('UserProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    managed_projects = db.relationship('Project', back_populates='manager', foreign_keys='Project.manager_id')
    managed_tasks = db.relationship('Task', back_populates='manager', foreign_keys='Task.manager_id')
    assigned_tasks = db.relationship('Task', back_populates='assignee', foreign_keys='Task.assigned_to_user_id')
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    team_memberships = db.relationship('TeamMember', back_populates='user', cascade='all, delete-orphan')
    managed_teams = db.relationship('Team', back_populates='manager', foreign_keys='Team.manager_id')
