from flask import render_template, abort ,request, redirect, url_for, flash, session, jsonify
from datetime import datetime
from models import db
from models.login_info import LoginInfo
from models.project import Project
from models.task import Task, CompletionStatus, SubtaskType, SubTask
from models.team import Team
from models.team_project import TeamProject
from models.team_member import TeamMember, TeamRole
from models.notification import Notification
from models.sprints import Sprint, SprintStatus
from .decorators import manager_required
from sqlalchemy.orm import joinedload


@manager_required
def manager_dashboard():
    user_id = session.get('user_id')
    team = Team.query.filter_by(manager_id=user_id).first()
    if not team:
        flash("You are not assigned as a manager.")
        return redirect(url_for('auth.login_page'))

    project_ids = [tp.project_id for tp in team.shared_projects]
    projects = Project.query.filter(Project.id.in_(project_ids), Project.is_deleted == False).all()
    
    # Get all sprints for manager's projects
    sprints = Sprint.query.filter(Sprint.project_id.in_(project_ids)).order_by(Sprint.start_date.desc()).all()
    today = datetime.utcnow().date()
    
    return render_template('manager/dashboard.html', team=team, projects=projects, sprints=sprints, today=today)


@manager_required
def create_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        summary = request.form.get('summary')
        deadline_str = request.form.get('deadline')
        user_id = session.get('user_id')

        team = Team.query.filter_by(manager_id=user_id).first()
        if not team:
            flash("You are not assigned as a manager.")
            return redirect(url_for('manager.manager_dashboard'))

        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date() if deadline_str else None
        except ValueError:
            flash("Invalid deadline format. Please use YYYY-MM-DD.")
            return redirect(url_for('manager.create_project'))

        project = Project(
            name=name,
            summary=summary,
            description=description,
            deadline=deadline,
            created_at=datetime.utcnow(),
            manager_id=team.manager_id,
            owner_team_id=team.id
        )

        db.session.add(project)
        db.session.commit()

        db.session.add(TeamProject(project_id=project.id, team_id=team.id))
        db.session.commit()

        flash('Project created successfully.')
        return redirect(url_for('manager.manager_dashboard'))

    return render_template('manager/create_project.html')


@manager_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    user_id = session.get('user_id')
    if project.manager_id != user_id:
        flash('You are not authorized to edit this project.')
        return redirect(url_for('manager.manager_dashboard'))

    if request.method in ['POST', 'PUT']:
        project.name = request.form.get('name')
        project.summary = request.form.get('summary')
        project.description = request.form.get('description')
        deadline_str = request.form.get('deadline')

        try:
            project.deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date() if deadline_str else None
        except ValueError:
            flash("Invalid deadline format. Please use YYYY-MM-DD.")
            return redirect(url_for('manager.edit_project', project_id=project_id))

        db.session.commit()
        flash('Project updated.')
        return redirect(url_for('manager.manager_dashboard'))

    return render_template('manager/edit_project.html', project=project)


@manager_required
def restore_project(project_id):
    project = Project.query.get_or_404(project_id)

    if project.manager_id != session.get('user_id'):
        abort(403)

    project.is_deleted = False
    db.session.commit()
    flash("Project restored.")
    return redirect(url_for('manager.manager_dashboard'))


@manager_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.is_deleted = True
    db.session.commit()
    flash('Project deleted.')
    return redirect(url_for('manager.manager_dashboard'))


@manager_required
def team_details():
    user_id = session.get('user_id')

    manager_record = TeamMember.query.filter_by(user_id=user_id).first()

    team_id = manager_record.team_id

    members = TeamMember.query.filter_by(team_id=team_id).join(LoginInfo).all()

    return render_template('manager/team_detail.html', members=members)


@manager_required
def edit_team():
    user_id = session.get('user_id')
    team = Team.query.filter_by(manager_id=user_id).first()
    
    if not team:
        flash("You are not assigned as a manager.")
        return redirect(url_for('manager.manager_dashboard'))

    if request.method in ['POST', 'PUT']:
        selected_user_ids = request.form.getlist('member_ids')
        selected_user_ids = set(map(int, selected_user_ids))

        current_member_ids = {member.user_id for member in TeamMember.query.filter_by(team_id=team.id).all()}

        # Add new members
        for user_id_to_add in selected_user_ids - current_member_ids:
            db.session.add(TeamMember(user_id=user_id_to_add, team_id=team.id, role=TeamRole.developer))

        # Remove members (except manager)
        for user_id_to_remove in current_member_ids - selected_user_ids:
            if user_id_to_remove != team.manager_id:
                TeamMember.query.filter_by(user_id=user_id_to_remove, team_id=team.id).delete()

        db.session.commit()
        flash('Team members updated successfully!')
        return redirect(url_for('manager.team_details'))

    team_members = TeamMember.query.filter_by(team_id=team.id).all()
    all_developers = LoginInfo.query.filter_by(is_deleted=False).all()

    return render_template('manager/edit_team.html', team=team,
                           members=team_members,
                           all_developers=all_developers)


@manager_required
def grant_project_access(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        team_id = request.form.get('team_id')

        try:
            team_id = int(team_id)
        except (TypeError, ValueError):
            flash("Invalid team ID.")
            return redirect(url_for('manager.view_project_details', project_id=project.id))

        existing_link = TeamProject.query.filter_by(project_id=project.id, team_id=team_id).first()
        if not existing_link:
            team = Team.query.get(team_id)
            if team:
                link = TeamProject(team=team, project=project)
                db.session.add(link)
                db.session.commit()
                flash('Access granted to selected team.')
            else:
                flash("Selected team does not exist.")
        else:
            flash("This team already has access.")

    return redirect(url_for('manager.view_project_details', project_id=project.id))


@manager_required
def create_task(project_id):
    users = LoginInfo.query.join(TeamMember).filter(TeamMember.role == TeamRole.developer).all()

    if request.method == 'POST':
        assigned_user_id = int(request.form['assigned_to'])
        task = Task(
            task_name=request.form['name'],
            summary=request.form['summary'],
            description=request.form['description'],
            project_id=project_id,
            manager_id=session['user_id'],
            assigned_to_user_id=assigned_user_id,
            completion_status=CompletionStatus.to_do,
            due_date=datetime.strptime(request.form['due_date'], "%Y-%m-%d"),
            created_at=datetime.utcnow()
        )
        db.session.add(task)
        db.session.flush()  # Get task.id before commit
        
        # Create notification for assigned user
        notification = Notification(
            user_id=assigned_user_id,
            description=f"You have been assigned to task: {task.task_name}",
            notification_type='task_assigned',
            related_task_id=task.id,
            action_url=url_for('developer.view_task_details', task_id=task.id),
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Task created and notification sent.')
        return redirect(url_for('manager.manager_dashboard'))

    return render_template('manager/create_task.html', project_id=project_id, users=users)


@manager_required
def restore_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.manager_id != session.get('user_id'):
        abort(403)

    task.is_deleted = False
    db.session.commit()
    flash("Task restored.")
    return redirect(url_for('manager.view_project', project_id=task.project_id))


@manager_required
def create_subtask(project_id):
    user_id = session.get('user_id')

    parent_tasks = Task.query.filter_by(
        project_id=project_id,
        manager_id=user_id,
        is_deleted=False
    ).all()

    if request.method == 'POST':
        name = request.form.get('name')
        status = request.form.get('status') or CompletionStatus.to_do.value
        subtask_type = request.form.get('type') or SubtaskType.feature.value
        due_date_str = request.form.get('due_date')
        parent_task_id = request.form.get('parent_task_id')

        if not name or not parent_task_id:
            flash("Name and parent task are required.")
            return redirect(request.url)

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None
        except ValueError:
            flash("Invalid due date format.")
            return redirect(request.url)

        subtask = SubTask(
            name=name,
            status=CompletionStatus(status),
            type=SubtaskType(subtask_type),
            due_date=due_date,
            parent_task_id=int(parent_task_id),
            created_at=datetime.utcnow()
        )

        db.session.add(subtask)
        db.session.commit()
        flash("Subtask created successfully.")
        return redirect(url_for('manager.view_project_details', project_id=project_id))

    return render_template(
        'manager/create_subtask.html',
        project_id=project_id,
        parent_tasks=parent_tasks,
        CompletionStatus=CompletionStatus,
        SubtaskType=SubtaskType
    )


@manager_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        new_status = request.form.get('status')
        
        # print("New Status Received:", new_status)
        # print("Request Type:", request.headers.get('X-Requested-With'))

        try:
            task.completion_status = CompletionStatus(new_status)
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return "Success", 200
            flash('Task status updated.')
        except ValueError:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return "Invalid status", 400
            flash('Invalid status.')
        return redirect(url_for('manager.manager_dashboard'))

    return render_template('manager/update_status.html', task=task, statuses=[status.name for status in CompletionStatus])


@manager_required
def task_details(task_id):
    task = Task.query.get_or_404(task_id)


    subtasks = SubTask.query.filter_by(parent_task_id=task.id, is_deleted=False).all()


    kanban_columns = {
        'completed': [],
        'in_progress': [],
        'failed': [],
        'to_do': []
    }

    for sub in subtasks:
        kanban_columns[sub.status.value].append(sub)


    return render_template('manager/task_details.html', task=task, kanban_columns=kanban_columns)

@manager_required
def update_subtask_status(subtask_id):
    from models import SubTask, db
    from models.task import CompletionStatus
    data = request.get_json()

    new_status_str = data.get('new_status')
    # print("Received:", subtask_id, new_status_str) 

    if not new_status_str:
        return jsonify({'success': False, 'message': 'Missing status'}), 400

    subtask = SubTask.query.get(subtask_id)
    if not subtask:
        return jsonify({'success': False, 'message': 'Subtask not found'}), 404

    try:
        new_status_enum = CompletionStatus(new_status_str)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400

    subtask.completion_status = new_status_enum
    db.session.commit()

    # print(f"Subtask {subtask_id} status updated to {new_status_enum}")
    return jsonify({'success': True, 'message': 'Status updated'})




@manager_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    users = LoginInfo.query.join(TeamMember).filter(TeamMember.role == TeamRole.developer).all()

    if request.method in ['POST', 'PUT']:
        task.task_name = request.form.get('name')
        task.summary = request.form.get('summary')
        task.description = request.form.get('description')
        task.assigned_to_user_id = int(request.form.get('assigned_to'))
        task.due_date = datetime.strptime(request.form.get('due_date'), "%Y-%m-%d")
        db.session.commit()
        flash('Task updated.')
        return redirect(url_for('manager.manager_dashboard'))

    return render_template('manager/edit_task.html', task=task, users=users)


@manager_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.is_deleted = True
    db.session.commit()
    flash('Task deleted.')
    return redirect(url_for('manager.manager_dashboard'))


@manager_required
def view_project_details(project_id):
    user_id = session.get('user_id')

    project = Project.query.filter_by(id=project_id, is_deleted=False).first_or_404()

    team = Team.query.filter_by(manager_id=user_id).first()
    if not team or project.owner_team_id != team.id:
        flash("You are not authorized to view this project.")
        return redirect(url_for('manager.manager_dashboard'))

    tasks = Task.query.filter_by(project_id=project_id)\
        .join(LoginInfo, Task.assigned_to_user_id == LoginInfo.id)\
        .add_entity(LoginInfo).all()

    access_teams = Team.query\
        .join(TeamProject, Team.id == TeamProject.team_id)\
        .filter(TeamProject.project_id == project_id, Team.id != project.owner_team_id)\
        .all()
    all_teams = Team.query.all()
    
    sprints = Sprint.query.filter_by(project_id=project_id).order_by(Sprint.start_date).all()

    return render_template(
        'manager/project_detail.html',
        project=project,
        tasks=tasks,
        all_teams=all_teams,
        access_teams=access_teams,
        sprints=sprints
    )

@manager_required
def create_sprint(project_id):
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, is_deleted=False, manager_id=user_id).first_or_404()
    
    if request.method == 'POST':
        name = request.form.get('name')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        status_str = request.form.get('status', 'planning')
        
        if not name or not start_date_str or not end_date_str:
            flash("All fields are required.")
            return redirect(request.url)
        
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            if end_date <= start_date:
                flash("End date must be after start date.")
                return redirect(request.url)
            
            # Convert status string to enum
            status = SprintStatus[status_str]
            
            sprint = Sprint(
                name=name,
                start_date=start_date,
                end_date=end_date,
                status=status,
                project_id=project_id,
                created_at=datetime.utcnow()
            )
            
            db.session.add(sprint)
            db.session.commit()
            flash(f'Sprint "{name}" created successfully!')
            return redirect(url_for('manager.view_project_details', project_id=project_id))
            
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return redirect(request.url)
    
    return render_template('manager/create_sprint.html', project=project)


@manager_required
def edit_sprint(sprint_id):
    user_id = session.get('user_id')
    sprint = Sprint.query.get_or_404(sprint_id)
    
    # Verify manager owns the project
    project = Project.query.filter_by(id=sprint.project_id, manager_id=user_id, is_deleted=False).first_or_404()
    
    if request.method == 'POST':
        name = request.form.get('name')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        status_str = request.form.get('status')
        
        if not name or not start_date_str or not end_date_str or not status_str:
            flash("All fields are required.")
            return redirect(request.url)
        
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            if end_date <= start_date:
                flash("End date must be after start date.")
                return redirect(request.url)
            
            # Update sprint
            sprint.name = name
            sprint.start_date = start_date
            sprint.end_date = end_date
            sprint.status = SprintStatus[status_str]
            
            db.session.commit()
            flash(f'Sprint "{name}" updated successfully!')
            return redirect(url_for('manager.view_sprint_detail', sprint_id=sprint_id))
            
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return redirect(request.url)
    
    return render_template('manager/edit_sprint.html', sprint=sprint, project=project)


@manager_required
def remove_task_from_sprint(task_id):
    user_id = session.get('user_id')
    task = Task.query.get_or_404(task_id)
    
    # Verify manager owns the project
    project = Project.query.filter_by(id=task.project_id, manager_id=user_id, is_deleted=False).first_or_404()
    
    if not task.sprint_id:
        flash("Task is not assigned to any sprint.")
        return redirect(request.referrer or url_for('manager.view_project_details', project_id=project.id))
    
    sprint_id = task.sprint_id
    sprint_name = task.sprint.name if task.sprint else "sprint"
    
    # Remove task from sprint
    task.sprint_id = None
    db.session.commit()
    
    flash(f'Task "{task.task_name}" removed from {sprint_name}.')
    
    # Redirect back to sprint detail if coming from there, otherwise to project
    if request.referrer and f'/sprints/{sprint_id}' in request.referrer:
        return redirect(url_for('manager.view_sprint_detail', sprint_id=sprint_id))
    else:
        return redirect(url_for('manager.view_project_details', project_id=project.id))


@manager_required
def assign_tasks_to_sprint(project_id):
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, is_deleted=False, manager_id=user_id).first_or_404()
    
    if request.method == 'POST':
        sprint_id = request.form.get('sprint_id')
        task_ids = request.form.getlist('task_ids')
        
        if not sprint_id:
            flash("Please select a sprint.")
            return redirect(request.url)
        
        sprint_id = int(sprint_id)
        sprint = Sprint.query.filter_by(id=sprint_id, project_id=project_id).first()
        
        if not sprint:
            flash("Invalid sprint selected.")
            return redirect(request.url)
        
        # Track tasks that are being moved from other sprints
        moved_count = 0
        assigned_count = 0
        
        # Update tasks with sprint_id
        for task_id in task_ids:
            task = Task.query.get(int(task_id))
            if task and task.project_id == project_id:
                if task.sprint_id and task.sprint_id != sprint_id:
                    moved_count += 1
                elif not task.sprint_id:
                    assigned_count += 1
                task.sprint_id = sprint_id
        
        db.session.commit()
        
        # Create informative flash message
        if moved_count > 0 and assigned_count > 0:
            flash(f'✅ {assigned_count} task(s) assigned and {moved_count} task(s) moved to sprint: {sprint.name}')
        elif moved_count > 0:
            flash(f'✅ {moved_count} task(s) moved to sprint: {sprint.name}')
        else:
            flash(f'✅ {assigned_count} task(s) assigned to sprint: {sprint.name}')
            
        return redirect(url_for('manager.view_project_details', project_id=project_id))
    
    # GET: Show form
    sprints = Sprint.query.filter_by(project_id=project_id).all()
    tasks = Task.query.filter_by(project_id=project_id, is_deleted=False).all()
    
    return render_template('manager/assign_tasks_to_sprint.html',
                           project=project,
                           sprints=sprints,
                           tasks=tasks)


@manager_required
def view_sprint_detail(sprint_id):
    user_id = session.get('user_id')
    sprint = Sprint.query.get_or_404(sprint_id)
    
    project = Project.query.filter_by(id=sprint.project_id, manager_id=user_id, is_deleted=False).first_or_404()
    
    sprint_tasks = Task.query.filter_by(sprint_id=sprint_id, is_deleted=False)\
        .join(LoginInfo, Task.assigned_to_user_id == LoginInfo.id)\
        .add_entity(LoginInfo).all()
    
    return render_template('manager/sprint_detail.html',
                         sprint=sprint,
                         project=project,
                         tasks=sprint_tasks)


@manager_required
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('auth.login_page'))

@manager_required
def view_developer_detail(developer_id):
    developer = LoginInfo.query.options(joinedload(LoginInfo.profile)).get_or_404(developer_id)

    assigned_tasks = Task.query.filter_by(assigned_to_user_id=developer.id).all()

    team_ids = [membership.team_id for membership in developer.team_memberships]
    assigned_teams = Team.query.filter(Team.id.in_(team_ids)).all()

    assigned_projects = (
        Project.query
        .join(TeamProject)
        .filter(TeamProject.team_id.in_(team_ids))
        .all()
    )

    return render_template(
        'manager/developer_detail.html',
        developer=developer,
        assigned_tasks=assigned_tasks,
        assigned_teams=assigned_teams,
        assigned_projects=assigned_projects
    )