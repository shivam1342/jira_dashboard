from models import db
from datetime import datetime
import enum

class NoteType(enum.Enum):
    query = 'query'
    issue = 'issue'
    comment = 'comment'

class Note(db.Model):
    __tablename__ = 'note'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    note_type = db.Column(db.Enum(NoteType))
    content = db.Column(db.Text)
    text = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('login_info.id'), nullable=False)
    parent_note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=True)
    is_resolved = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    task = db.relationship('Task', back_populates='notes')
    creator = db.relationship('LoginInfo', foreign_keys=[created_by])
    replies = db.relationship('Note', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
