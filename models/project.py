from models import db
from datetime import datetime
from sqlalchemy.orm import backref

class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    summary = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.Date)
    is_approved = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)

    manager_id = db.Column(db.Integer, db.ForeignKey('login_info.id', ondelete='SET NULL'))
    owner_team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), nullable=False)

    manager = db.relationship('LoginInfo', back_populates='managed_projects', foreign_keys=[manager_id])
    owning_team = db.relationship('Team', back_populates='projects', foreign_keys=[owner_team_id])
    tasks = db.relationship('Task', backref=backref('project', passive_deletes=True), cascade='all, delete-orphan', passive_deletes=True)
    team_links = db.relationship('TeamProject', back_populates='project', cascade='all, delete-orphan', passive_deletes=True)
