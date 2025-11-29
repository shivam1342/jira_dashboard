from models import db

class TeamProject(db.Model):
    __tablename__ = 'team_project'

    team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), primary_key=True)

    team = db.relationship('Team', back_populates='shared_projects')
    project = db.relationship('Project', back_populates='team_links')
