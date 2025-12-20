from models import db
from datetime import datetime
import enum

class CompletionStatus(enum.Enum):
    completed = 'completed'
    in_progress = 'in_progress'
    failed = 'failed'
    to_do = 'to_do'

class PriorityLevel(enum.Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'

class SubtaskType(enum.Enum):
    bug = 'bug'
    update = 'update'
    feature = 'feature'
    test = 'test'

class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(120), nullable=False)
    summary = db.Column(db.String(255))
    description = db.Column(db.Text)
    priority = db.Column(db.Enum(PriorityLevel), default=PriorityLevel.low, nullable=False)
    completion_status = db.Column(db.Enum(CompletionStatus), default=CompletionStatus.to_do, nullable=False)
    due_date = db.Column(db.Date)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('login_info.id', ondelete='SET NULL'), nullable=True)
    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('login_info.id', ondelete='SET NULL'), nullable=True)
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprint.id', ondelete='SET NULL'), nullable=True)

    manager = db.relationship('LoginInfo', back_populates='managed_tasks', foreign_keys=[manager_id])
    assignee = db.relationship('LoginInfo', back_populates='assigned_tasks', foreign_keys=[assigned_to_user_id])
    sprint = db.relationship('Sprint', backref='tasks')
    notes = db.relationship('Note', back_populates='task', cascade='all, delete-orphan')


class SubTask(db.Model):
    __tablename__ = 'sub_task'

    id = db.Column(db.Integer, primary_key=True)
    parent_task_id = db.Column(db.Integer, db.ForeignKey('task.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.Enum(CompletionStatus), default=CompletionStatus.to_do, nullable=False)
    type = db.Column(db.Enum(SubtaskType), default=SubtaskType.feature, nullable=False)
    due_date = db.Column(db.Date)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    parent_task = db.relationship('Task', backref=db.backref('subtasks', cascade='all, delete-orphan', passive_deletes=True))