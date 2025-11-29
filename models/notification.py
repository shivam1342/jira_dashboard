from models import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('login_info.id'), nullable=False)
    description = db.Column(db.Text)
    notification_type = db.Column(db.String(50))  # 'task_assigned', 'query_raised', 'status_changed', etc.
    related_task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    action_url = db.Column(db.String(255))  # Direct link to task/project
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('LoginInfo', back_populates='notifications')
    task = db.relationship('Task', backref='notifications')
