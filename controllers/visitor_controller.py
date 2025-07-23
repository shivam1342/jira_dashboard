from flask import render_template, request, redirect, url_for, session, flash
from models import db
from models.project import Project
from models.task import Task, CompletionStatus
from models.team_project import TeamProject
from models.team_member import TeamMember
from models.team import Team
from models.login_info import LoginInfo
from models.note import Note
from datetime import datetime


def view_approved_projects():
    visitor_id = session.get('user_id')

    team_ids = [tm.team_id for tm in TeamMember.query.filter_by(user_id=visitor_id).all()]

    project_ids = [tp.project_id for tp in TeamProject.query.filter(TeamProject.team_id.in_(team_ids)).all()]

    projects = Project.query.filter(
        Project.id.in_(project_ids),
        Project.is_deleted == False
    ).all()

    return render_template('visitor/view_projects.html', projects=projects)


def view_project_detail(project_id):
    project = Project.query.filter_by(id=project_id, is_deleted=False).first_or_404()

    team_project = TeamProject.query.filter_by(project_id=project.id).first()
    team = team_project.team if team_project and not team_project.team.is_deleted else None
    members = TeamMember.query.filter_by(team_id=team.id).all() if team else []

    tasks = Task.query.filter_by(project_id=project.id, is_deleted=False).all()
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.completion_status == CompletionStatus.completed])
    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    return render_template('visitor/project_detail.html', project=project, team=team, members=members,
                           tasks=tasks, progress_percentage=progress_percentage)


def submit_feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        note = Note(
            sender_id=None, 
            receiver_id=None,  
            content=f"[Visitor: {name}, Email: {email}]\n{message}",
            timestamp=datetime.utcnow()
        )
        db.session.add(note)
        db.session.commit()
        flash("Feedback submitted successfully.")
        return redirect(url_for('visitor.view_approved_projects'))

    return render_template('visitor/feedback.html')
