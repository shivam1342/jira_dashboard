from models import db
from datetime import datetime

class UserProfile(db.Model):
    __tablename__ = 'user_profile'

    id = db.Column(db.Integer, primary_key=True)
    login_info_id = db.Column(db.Integer, db.ForeignKey('login_info.id', ondelete='CASCADE'), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    gmail = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    gender = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('LoginInfo', back_populates='profile')
