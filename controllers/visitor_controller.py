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


def visitor_dashboard():
    visitor_id = session.get('user_id')
    
    # Get team IDs for the visitor
    team_ids = [tm.team_id for tm in TeamMember.query.filter_by(user_id=visitor_id).all()]
    
    # Get project IDs from team projects
    project_ids = [tp.project_id for tp in TeamProject.query.filter(TeamProject.team_id.in_(team_ids)).all()]
    
    # Get projects
    projects = Project.query.filter(
        Project.id.in_(project_ids),
        Project.is_deleted == False
    ).all()
    
    # Get tasks for these projects
    tasks = Task.query.filter(
        Task.project_id.in_(project_ids),
        Task.is_deleted == False
    ).all()
    
    # Get unique team members count
    team_members_count = db.session.query(TeamMember).filter(
        TeamMember.team_id.in_(team_ids)
    ).distinct(TeamMember.user_id).count()
    
    # Get recent projects (last 3)
    recent_projects = projects[:3] if projects else []
    
    return render_template('visitor/dashboard.html', 
                          project_count=len(projects),
                          task_count=len(tasks),
                          team_count=team_members_count,
                          recent_projects=recent_projects)


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
            content=f"[Visitor Feedback]\nName: {name}\nEmail: {email}\n\nMessage:\n{message}",
            timestamp=datetime.utcnow()
        )
        db.session.add(note)
        db.session.commit()
        flash("Thank you for your feedback! We appreciate your input.", "success")
        return redirect(url_for('visitor.submit_feedback'))

    return render_template('visitor/feedback.html')
