from flask import render_template, request, redirect, url_for, session, flash, jsonify
from models import db
from models.project import Project
from models.task import Task, CompletionStatus, SubtaskType, SubTask
from models.login_info import LoginInfo
from models.team_member import TeamMember
from models.team import Team
from models.team_project import TeamProject
from datetime import datetime
from .decorators import developer_required
from sqlalchemy.orm import joinedload


@developer_required
def developer_dashboard():
    user_id = session.get('user_id')

    member = TeamMember.query.filter_by(user_id=user_id).first()
    team_id = member.team_id if member else None

    projects = Project.query \
        .join(Project.team_links) \
        .join(TeamProject.team) \
        .join(Team.members) \
        .filter(LoginInfo.id == user_id) \
        .filter(Project.is_deleted == False) \
        .distinct().all()

    total_tasks = Task.query.filter_by(assigned_to_user_id=user_id).count()
    completed_tasks = Task.query.filter_by(
        assigned_to_user_id=user_id,
        completion_status=CompletionStatus.completed
    ).count()
    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    is_team_manager = False
    if team_id:
        team = Team.query.get(team_id)
        if team and team.manager_id == user_id:
            is_team_manager = True

    return render_template('developer/dashboard.html',
                           projects=projects,
                           total_tasks=total_tasks,
                           completed_tasks=completed_tasks,
                           progress_percentage=progress_percentage,
                           is_team_manager=is_team_manager)


@developer_required
def view_project_details(project_id):
    user_id = session.get('user_id')

    project = Project.query \
        .join(Project.team_links) \
        .join(TeamProject.team) \
        .join(Team.members) \
        .filter(Project.id == project_id,
                LoginInfo.id == user_id,
                Project.is_deleted == False) \
        .first()

    if not project:
        flash("You don't have access to this project.")
        return redirect(url_for('developer.view_projects'))

    all_tasks = Task.query.filter_by(project_id=project_id).all()
    own_tasks = Task.query.filter_by(project_id=project_id, assigned_to_user_id=user_id).all()
    subtasks = SubTask.query \
        .join(SubTask.parent_task) \
        .filter(Task.project_id == project_id,
                Task.assigned_to_user_id == user_id,
                SubTask.is_deleted == False) \
        .all()

    return render_template('developer/project_details.html',
                           project=project,
                           all_tasks=all_tasks,
                           own_tasks=own_tasks,
                           subtasks=subtasks,
                           statuses=[status.name for status in CompletionStatus])


@developer_required
def view_task_details(task_id):
    user_id = session.get('user_id')

    task = Task.query \
        .options(joinedload(Task.subtasks)) \
        .filter_by(id=task_id, is_deleted=False) \
        .first()

    if not task:
        flash("Task not found.")
        return redirect(url_for('developer.developer_dashboard'))

    if task.assigned_to_user_id != user_id:
        project = Project.query \
            .join(Project.team_links) \
            .join(TeamProject.team) \
            .join(Team.members) \
            .filter(Project.id == task.project_id,
                    LoginInfo.id == user_id) \
            .first()

        if not project:
            flash("You do not have access to this task.")
            return redirect(url_for('developer.developer_dashboard'))

    subtasks = SubTask.query.filter_by(parent_task_id=task_id).all()

    return render_template('developer/task_details.html',
                           task=task,
                           subtasks=subtasks,
                           statuses=[status.name for status in CompletionStatus],
                           types=[stype.name for stype in SubtaskType])


@developer_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)

    if task.assigned_to_user_id != session.get('user_id'):
        flash("You cannot update this task.")
        return redirect(url_for('developer.developer_dashboard'))

    if request.method == 'POST':
        new_status = request.form.get('status')
        try:
            task.completion_status = CompletionStatus(new_status)
            db.session.commit()
            flash('Task status updated.')
        except ValueError:
            flash('Invalid status value.')
        return redirect(url_for('developer.view_project_details', project_id=task.project_id))

    return render_template('developer/update_status.html',
                           task=task,
                           statuses=[status.name for status in CompletionStatus])


@developer_required
def update_task_status_api(task_id):
    from models import Task, db
    from models.task import CompletionStatus

    task = Task.query.get_or_404(task_id)

    print("Session user ID:", session.get('user_id'))
    print("Assigned to user ID:", task.assigned_to_user_id)

    if task.assigned_to_user_id != session.get('user_id'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    new_status = data.get('status')

    if not new_status:
        return jsonify({'success': False, 'message': 'Missing status'}), 400

    try:
        task.completion_status = CompletionStatus(new_status.lower())

        db.session.commit()
        return jsonify({'success': True})
    except (ValueError, KeyError) as e:
        print("Enum conversion error:", e)
        return jsonify({'success': False, 'message': 'Invalid status'}), 400


@developer_required
def create_task():
    user_id = session.get('user_id')

    if request.method == 'POST':
        name = request.form.get('task_name')
        summary = request.form.get('summary')
        description = request.form.get('description')
        project_id = int(request.form.get('project_id'))
        due_date = request.form.get('due_date')

        member = TeamMember.query.filter_by(user_id=user_id).first()
        team = Team.query.get(member.team_id) if member else None

        if not team or not team.manager_id:
            flash("You are not part of a valid team or team has no manager.")
            return redirect(url_for('developer.view_project_details'))

        task = Task(
            task_name=name,
            summary=summary,
            description=description,
            project_id=project_id,
            manager_id=team.manager_id,
            assigned_to_user_id=user_id,
            completion_status=CompletionStatus.to_do,
            due_date=datetime.strptime(due_date, "%Y-%m-%d") if due_date else None,
            created_at=datetime.utcnow()
        )
        db.session.add(task)
        db.session.commit()
        flash("Task created successfully.")
        return redirect(url_for('developer.view_project_details', project_id=project_id))

    projects = Project.query \
        .join(Project.team_links) \
        .join(TeamProject.team) \
        .join(Team.members) \
        .filter(LoginInfo.id == user_id, Project.is_deleted == False) \
        .distinct() \
        .all()

    return render_template('developer/create_task.html', projects=projects)


@developer_required
def create_subtask(project_id):
    user_id = session.get('user_id')

    project = Project.query \
        .join(Project.team_links) \
        .join(TeamProject.team) \
        .join(Team.members) \
        .filter(Project.id == project_id,
                LoginInfo.id == user_id,
                Project.is_deleted == False) \
        .first()

    if not project:
        flash("You don't have permission to add a subtask to this project.")
        return redirect(url_for('developer.view_projects'))

    tasks = Task.query.filter_by(project_id=project_id, assigned_to_user_id=user_id).all()

    if request.method == 'POST':
        name = request.form.get('name')
        parent_task_id = request.form.get('parent_task_id')
        due_date = request.form.get('due_date')
        status = request.form.get('status') or 'to_do'
        subtask_type = request.form.get('type') or 'feature'

        subtask = SubTask(
            name=name,
            parent_task_id=int(parent_task_id),
            status=CompletionStatus[status],
            type=SubtaskType[subtask_type],
            due_date=datetime.strptime(due_date, "%Y-%m-%d") if due_date else None,
        )

        db.session.add(subtask)
        db.session.commit()

        flash("Subtask created successfully.")
        return redirect(url_for('developer.view_project_details', project_id=project_id))

    return render_template('developer/create_subtask.html', project=project, tasks=tasks)

@developer_required
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('auth.login_page'))