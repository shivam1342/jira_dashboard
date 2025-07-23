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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
