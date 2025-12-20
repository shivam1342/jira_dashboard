

from models import db
from datetime import datetime
import enum

class SprintStatus(enum.Enum):
    planning = "Planning"
    active = "Active"
    completed = "Completed"
    archived = "Archived"

class Sprint(db.Model):
    __tablename__ = 'sprint'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(SprintStatus), default=SprintStatus.planning, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project = db.relationship('Project', backref='sprints') 
