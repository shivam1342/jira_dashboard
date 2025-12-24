from flask import render_template, request, redirect, url_for, session, flash, jsonify, current_app
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

    # Get ALL teams the user is a member of (not just the first one)
    team_memberships = TeamMember.query.filter_by(user_id=user_id).all()
    team_ids = [tm.team_id for tm in team_memberships]

    # Show projects where:
    # 1. User is the manager (manager_id == user_id)
    projects_as_manager = Project.query.filter_by(manager_id=user_id, is_deleted=False).all()
    
    # 2. User has assigned tasks (as developer)
    projects_with_tasks = Project.query \
        .join(Task, Task.project_id == Project.id) \
        .filter(Task.assigned_to_user_id == user_id) \
        .filter(Project.is_deleted == False) \
        .distinct().all()
    
    # 3. User is a member of team(s) that have access to projects
    projects_via_team = []
    if team_ids:
        projects_via_team = Project.query \
            .join(TeamProject, TeamProject.project_id == Project.id) \
            .filter(TeamProject.team_id.in_(team_ids)) \
            .filter(Project.is_deleted == False) \
            .all()
    
    # Combine all three lists and remove duplicates
    project_ids_seen = set()
    projects = []
    for project in projects_as_manager + projects_with_tasks + projects_via_team:
        if project.id not in project_ids_seen:
            projects.append(project)
            project_ids_seen.add(project.id)

    total_tasks = Task.query.filter_by(assigned_to_user_id=user_id).count()
    completed_tasks = Task.query.filter_by(
        assigned_to_user_id=user_id,
        completion_status=CompletionStatus.completed
    ).count()
    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    is_team_manager = False
    for team_id in team_ids:
        team = Team.query.get(team_id)
        if team and team.manager_id == user_id:
            is_team_manager = True
            break

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


def update_task_status_api(task_id):
    """API endpoint for kanban drag-and-drop - CSRF exempt"""
    from models import Task, db
    from models.task import CompletionStatus

    print(f"[DEBUG] API called for task_id: {task_id}")
    print(f"[DEBUG] Session user_id: {session.get('user_id')}")
    print(f"[DEBUG] Request method: {request.method}")
    print(f"[DEBUG] Request headers: {dict(request.headers)}")
    
    # Check if user is authenticated
    if 'user_id' not in session:
        print("[DEBUG] No user_id in session - returning 401")
        return jsonify({'success': False, 'message': 'Unauthorized: Please log in'}), 401

    task = Task.query.get_or_404(task_id)
    print(f"[DEBUG] Task found: {task.task_name}")
    print(f"[DEBUG] Task assigned to: {task.assigned_to_user_id}")

    if task.assigned_to_user_id != session.get('user_id'):
        print("[DEBUG] User not authorized for this task - returning 403")
        return jsonify({'success': False, 'message': 'Unauthorized: You can only update tasks assigned to you'}), 403

    data = request.get_json()
    print(f"[DEBUG] Request data: {data}")
    new_status = data.get('status')
    print(f"[DEBUG] New status: {new_status}")

    if not new_status:
        print("[DEBUG] No status provided - returning 400")
        return jsonify({'success': False, 'message': 'Missing status'}), 400

    try:
        # Convert status string to enum using attribute access
        if hasattr(CompletionStatus, new_status):
            old_status = task.completion_status
            task.completion_status = getattr(CompletionStatus, new_status)
            print(f"[DEBUG] Status changed from {old_status} to {task.completion_status}")
        else:
            print(f"[DEBUG] Invalid status: {new_status}")
            return jsonify({'success': False, 'message': f'Invalid status: {new_status}'}), 400

        db.session.commit()
        print("[DEBUG] Database commit successful")
        return jsonify({'success': True, 'message': 'Task status updated successfully'})
    except Exception as e:
        print(f"[DEBUG] Exception occurred: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error updating task: {str(e)}'}), 500


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

def update_subtask_status_api(subtask_id):
    """API endpoint for subtask kanban drag-and-drop - CSRF exempt"""
    from models.task import CompletionStatus
    
    # Check if user is authenticated
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized: Please log in'}), 401
    
    user_id = session.get('user_id')
    subtask = SubTask.query.get_or_404(subtask_id)
    
    # Security check: Ensure the subtask's parent task is assigned to this developer
    if subtask.parent_task.assigned_to_user_id != user_id:
        return jsonify({'success': False, 'message': 'Unauthorized: You can only update subtasks from your own tasks'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'success': False, 'message': 'Missing status'}), 400
    
    try:
        # Convert status string to enum using attribute access
        if hasattr(CompletionStatus, new_status):
            subtask.status = getattr(CompletionStatus, new_status)
        else:
            return jsonify({'success': False, 'message': f'Invalid status: {new_status}'}), 400
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Subtask status updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error updating subtask: {str(e)}'}), 500

@developer_required
def edit_subtask(subtask_id):
    """Edit subtask details"""
    from forms import SubtaskForm
    from models.task import CompletionStatus
    
    user_id = session.get('user_id')
    subtask = SubTask.query.get_or_404(subtask_id)
    
    # Security check: Ensure the subtask's parent task is assigned to this developer
    if subtask.parent_task.assigned_to_user_id != user_id:
        flash("Unauthorized: You can only edit subtasks from your own tasks.")
        return redirect(url_for('developer.developer_dashboard'))
    
    form = SubtaskForm(obj=subtask)
    
    if form.validate_on_submit():
        subtask.name = form.name.data
        subtask.type = form.type.data
        subtask.status = form.status.data
        subtask.due_date = form.due_date.data
        
        db.session.commit()
        flash("Subtask updated successfully.")
        return redirect(url_for('developer.view_task_details', task_id=subtask.parent_task_id))
    
    return render_template('developer/edit_subtask.html', form=form, subtask=subtask)


@developer_required
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('auth.login_page'))