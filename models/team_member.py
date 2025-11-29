from models import db
import enum

class TeamRole(enum.Enum):
    developer = "developer"
    manager = "manager"
    visitor = "visitor"

class TeamMember(db.Model):
    __tablename__ = 'team_member'

    user_id = db.Column(db.Integer, db.ForeignKey('login_info.id', ondelete='CASCADE'), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), primary_key=True)
    role = db.Column(db.Enum(TeamRole), nullable=False, default=TeamRole.developer)

    user = db.relationship('LoginInfo', back_populates='team_memberships')
    team = db.relationship('Team', back_populates='members')
