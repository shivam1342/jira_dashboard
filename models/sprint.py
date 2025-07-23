
from models import db
from datetime import datetime

class Sprint(db.Model):
    __tablename__ = 'sprint'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    goal = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='sprint', lazy=True)
    
    # project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)

    
    # project = db.relationship('Project', backref=db.backref('sprints', cascade='all, delete-orphan'))
