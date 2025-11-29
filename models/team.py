from models import db
from datetime import datetime

class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('login_info.id', ondelete='SET NULL'), nullable=True)
    description = db.Column(db.Text)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    manager = db.relationship('LoginInfo', back_populates='managed_teams', foreign_keys=[manager_id])
    members = db.relationship('TeamMember', back_populates='team', cascade='all, delete-orphan', passive_deletes=True)
    projects = db.relationship('Project', back_populates='owning_team', cascade='all, delete-orphan', passive_deletes=True)
    shared_projects = db.relationship('TeamProject', back_populates='team', cascade='all, delete-orphan', passive_deletes=True)
