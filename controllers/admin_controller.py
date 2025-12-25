from flask import request, redirect, url_for, render_template, flash, session, current_app
from models import db
from models.team import Team
from models.login_info import LoginInfo, UserRole
from models.user_profile import UserProfile
from models.project import Project
from models.team_member import TeamMember, TeamRole
from models.task import Task, CompletionStatus
from models.notification import Notification
from .decorators import admin_required
from flask_mailman import EmailMessage
import bcrypt
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import os

@admin_required
def create_team():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            manager_id = request.form.get('manager_id')

            # Validation
            if not name:
                flash('Team name is required', 'error')
                return redirect(url_for('admin.show_create_team_form'))

            # Check for duplicate team name
            existing_team = Team.query.filter_by(name=name, is_deleted=False).first()
            if existing_team:
                flash(f'Team "{name}" already exists', 'error')
                current_app.logger.warning(f'Attempt to create duplicate team: {name}')
                return redirect(url_for('admin.show_create_team_form'))

            team = Team(name=name, description=description)

            if manager_id:
                team.manager_id = int(manager_id)

            db.session.add(team)
            db.session.commit()

            if manager_id:
                manager_id = int(manager_id)
                existing_member = TeamMember.query.filter_by(user_id=manager_id, team_id=team.id).first()
                if existing_member:
                    existing_member.role = TeamRole.manager
                else:
                    db.session.add(TeamMember(user_id=manager_id, team_id=team.id, role=TeamRole.manager))
                db.session.commit()

            current_app.logger.info(f'Team created: {name} (ID: {team.id}) by admin user {session.get("username")}')
            flash('Team created successfully!', 'success')
            return redirect(url_for('admin.admin_dashboard'))

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f'Database integrity error creating team: {str(e)}')
            flash('Error creating team: Duplicate name or invalid data', 'error')
            return redirect(url_for('admin.show_create_team_form'))
        except ValueError as e:
            db.session.rollback()
            current_app.logger.error(f'ValueError creating team: {str(e)}')
            flash('Invalid manager selection', 'error')
            return redirect(url_for('admin.show_create_team_form'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Unexpected error creating team: {str(e)}', exc_info=True)
            flash('An unexpected error occurred. Please try again.', 'error')
            return redirect(url_for('admin.show_create_team_form'))

    potential_managers = LoginInfo.query \
        .filter(LoginInfo.is_deleted == False) \
        .join(TeamMember) \
        .filter(TeamMember.role == TeamRole.developer) \
        .all()

    return render_template('admin/create_team.html', managers=potential_managers)

@admin_required
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)

    if request.method in ['POST', 'PUT']:
        team.name = request.form['name']
        team.description = request.form.get('description')
        new_manager_id = request.form.get('manager_id')

        if new_manager_id:
            new_manager_id = int(new_manager_id)
            team.manager_id = new_manager_id

            membership = TeamMember.query.filter_by(user_id=new_manager_id, team_id=team_id).first()
            if membership:
                membership.role = TeamRole.manager
            else:
                db.session.add(TeamMember(user_id=new_manager_id, team_id=team.id, role=TeamRole.manager))

        selected_user_ids = request.form.getlist('member_ids')
        selected_user_ids = set(map(int, selected_user_ids))

        current_member_ids = {member.user_id for member in TeamMember.query.filter_by(team_id=team_id).all()}

        for user_id in selected_user_ids - current_member_ids:
            db.session.add(TeamMember(user_id=user_id, team_id=team.id, role=TeamRole.developer))

        for user_id in current_member_ids - selected_user_ids:
            if user_id != team.manager_id:
                TeamMember.query.filter_by(user_id=user_id, team_id=team_id).delete()

        db.session.commit()
        flash('Team updated successfully!')
        return redirect(url_for('admin.admin_dashboard'))

    team_members = TeamMember.query.filter_by(team_id=team_id).all()
    all_developers = LoginInfo.query \
        .filter_by(is_deleted=False, role=UserRole.developer) \
        .all()

    return render_template('admin/edit_team.html', team=team,
                           members=team_members,
                           all_developers=all_developers)

@admin_required
def delete_team(team_id):
    try:
        team = Team.query.get_or_404(team_id)
        team.is_deleted = True
        db.session.commit()
        
        current_app.logger.info(f'Team archived: {team.name} (ID: {team_id}) by admin user {session.get("username")}')
        flash('Team archived successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error archiving team {team_id}: {str(e)}', exc_info=True)
        flash('Error archiving team. Please try again.', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_required
def view_team(team_id):
    team = Team.query.get_or_404(team_id)
    members = [tm.user for tm in team.members]
    return render_template("admin/view_team.html", team=team, members=members)

@admin_required
def view_users():
    approved_users = LoginInfo.query.filter(
        LoginInfo.is_deleted == False,
        LoginInfo.is_approved == True,
    ).all()

    unapproved_users = LoginInfo.query.filter(
        LoginInfo.is_deleted == False,
        LoginInfo.is_approved == False,
        LoginInfo.role != UserRole.visitor
    ).all()
    return render_template('admin/view_users.html', approved_users=approved_users, unapproved_users=unapproved_users)

@admin_required
def approve_user(user_id):
    try:
        user = LoginInfo.query.get_or_404(user_id)
        user.is_approved = True
        db.session.commit()

        # Send approval email
        try:
            subject = "You are approved by admin"
            message = f"Hello {user.username},\n\nYour Account has been approved by the admin."
            email = EmailMessage(subject, message, to=[user.profile.gmail])
            email.send()
            current_app.logger.info(f'Approval email sent to {user.profile.gmail}')
        except Exception as email_error:
            current_app.logger.warning(f'Failed to send approval email to {user.profile.gmail}: {str(email_error)}')
            # Don't fail the whole operation if email fails
        
        current_app.logger.info(f'User approved: {user.username} (ID: {user_id}) by admin {session.get("username")}')
        flash("User approved successfully.", 'success')
        return redirect(url_for('admin.view_users'))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error approving user {user_id}: {str(e)}', exc_info=True)
        flash('Error approving user. Please try again.', 'error')
        return redirect(url_for('admin.view_users'))

@admin_required
def edit_user(user_id):
    user = LoginInfo.query.get_or_404(user_id)

    if request.method in ['POST', 'PUT']:
        username = request.form.get('username')
        role = request.form.get('role')
        
        if not username or not role:
            flash('Username and role are required.', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        user.username = username
        user.role = UserRole(role)
        db.session.commit()
        flash('User updated successfully!')
        return redirect(url_for('admin.view_users'))

    return render_template('admin/edit_user.html', user=user)

@admin_required
def delete_user(user_id):
    try:
        user = LoginInfo.query.get_or_404(user_id)
        username = user.username
        user.is_deleted = True
        db.session.commit()
        
        current_app.logger.info(f'User deleted: {username} (ID: {user_id}) by admin {session.get("username")}')
        flash('User deleted successfully!', 'success')
        return redirect(url_for('admin.view_users'))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting user {user_id}: {str(e)}', exc_info=True)
        flash('Error deleting user. Please try again.', 'error')
        return redirect(url_for('admin.view_users'))
    flash('User soft-deleted.')
    return redirect(url_for('admin.view_users'))

@admin_required
def reset_password(user_id):
    if request.method == 'POST':
        new_password = request.form['password']
        user = LoginInfo.query.get_or_404(user_id)
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Password reset successfully.")
        return redirect(url_for('admin.view_users'))

    return render_template('admin/reset_password.html', user_id=user_id)

@admin_required
def reports():
    users = LoginInfo.query.all()
    teams = Team.query.filter_by(is_deleted=False).all()
    projects = Project.query.all()

    for project in projects:
        total_tasks = len(project.tasks)
        if total_tasks > 0:
            completed_tasks = sum(1 for task in project.tasks if task.completion_status.name == 'completed')
            project.is_completed = (total_tasks == completed_tasks)
        else:
            project.is_completed = False

    return render_template('admin/reports.html', users=users, teams=teams, projects=projects)

@admin_required
def project_report(project_id):
    project = Project.query.get_or_404(project_id)

    total_tasks = len(project.tasks)
    completed_tasks = sum(1 for t in project.tasks if t.completion_status.name == 'completed')
    progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    assigned_teams = [tp.team for tp in project.team_links]
    owner_team = assigned_teams[0] if assigned_teams else None

    task_info = [{
        'name': t.task_name,
        'status': t.completion_status.name,
        'assigned_to': t.assignee.profile.name if t.assignee and t.assignee.profile else 'Unassigned'
    } for t in project.tasks]

    return render_template('admin/project_report.html', project=project,
                           owner_team=owner_team,
                           assigned_teams=assigned_teams,
                           total_tasks=total_tasks,
                           completed_tasks=completed_tasks,
                           progress=round(progress, 2),
                           task_info=task_info)

@admin_required
def handle_visitors():
    visitors = LoginInfo.query.filter_by(role=UserRole.visitor, is_deleted=False, is_approved=False).all()
    projects = Project.query.all()
    return render_template('admin/visitors.html', visitors=visitors, projects=projects)

@admin_required
def approve_visitor():
    visitor_id = int(request.form['visitor_id'])
    project_id = int(request.form['project_id'])

    visitor = LoginInfo.query.get_or_404(visitor_id)
    project = Project.query.get_or_404(project_id)

    visitor.is_approved = True

    owner_team_link = project.team_links[0] if project.team_links else None

    if not owner_team_link:
        flash(f"Cannot assign project '{project.name}' — no owner team linked.")
        return redirect(url_for('admin.handle_visitors'))

    owner_team_id = owner_team_link.team_id

    existing_membership = TeamMember.query.filter_by(user_id=visitor.id, team_id=owner_team_id).first()
    if not existing_membership:
        db.session.add(TeamMember(user_id=visitor.id, team_id=owner_team_id, role=TeamRole.visitor))

    visitor.is_approved = True
    db.session.commit()

    subject = "You are approved by admin"
    message = f"Hello {visitor.username},\n\nYour Account has been approved by the admin."
    email = EmailMessage(subject, message, to=[visitor.profile.gmail])
    email.send()

    flash(f"Visitor '{visitor.username}' approved and added to project '{project.name}' team.")
    return redirect(url_for('admin.handle_visitors'))

@admin_required
def suspend_visitor(visitor_id):
    visitor = LoginInfo.query.get_or_404(visitor_id)
    visitor.is_deleted = True
    db.session.commit()
    flash("Visitor access suspended.")
    return redirect(url_for('admin.handle_visitors'))

@admin_required
def admin_dashboard():
    total_users = LoginInfo.query.filter_by(is_deleted=False).count()
    total_teams = Team.query.filter_by(is_deleted=False).count()
    total_projects = Project.query.count()

    all_teams = Team.query.filter_by(is_deleted=False).all()
    all_projects = Project.query.all()

    return render_template("admin/dashboard.html",
                           total_users=total_users,
                           total_teams=total_teams,
                           total_projects=total_projects,
                           teams=all_teams,
                           projects=all_projects)

@admin_required
def create_user():
    from sqlalchemy.exc import IntegrityError

    teams = Team.query.filter_by(is_deleted=False).all()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        name = request.form.get('name')
        gmail = request.form.get('gmail')
        phone = request.form.get('phone')
        team_id = request.form.get('team_id')
        
        # Validate required fields
        if not all([username, password, role, name]):
            flash('Username, password, role, and name are required.', 'error')
            return render_template('admin/create_user.html', teams=teams)

        try:
            # Hash the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            new_user = LoginInfo(
                username=username,
                password=hashed_password,
                role=UserRole(role),
                is_approved=True,
                is_deleted=False
            )
            db.session.add(new_user)
            db.session.flush()

            profile = UserProfile(
                login_info_id=new_user.id,
                name=name,
                gmail=gmail,
                phone=phone
            )
            db.session.add(profile)

            if team_id:
                db.session.add(TeamMember(
                    user_id=new_user.id,
                    team_id=int(team_id),
                    role=TeamRole[role] if role in TeamRole.__members__ else TeamRole.developer
                ))

            db.session.commit()
            flash('User created and assigned to team successfully!')
            return redirect(url_for('admin.view_users'))

        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please try a different one.')

    return render_template('admin/create_user.html', teams=teams)

@admin_required
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('auth.login'))


# ==================== LOGS & ACTIVITY TRACKING ====================

@admin_required
def system_logs():
    """View application system logs"""
    try:
        log_file_path = os.path.join(current_app.root_path, 'logs', 'app.log')
        logs = []
        
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r', encoding='utf-8') as f:
                # Read last 500 lines
                all_lines = f.readlines()
                recent_lines = all_lines[-500:] if len(all_lines) > 500 else all_lines
                
                for line in reversed(recent_lines):
                    if line.strip():
                        logs.append({
                            'timestamp': line[:23] if len(line) > 23 else '',
                            'level': 'ERROR' if 'ERROR' in line else 'WARNING' if 'WARNING' in line else 'INFO',
                            'message': line[24:] if len(line) > 24 else line
                        })
        
        return render_template('admin/system_logs.html', logs=logs)
    except Exception as e:
        current_app.logger.error(f'Error reading system logs: {str(e)}')
        flash('Error loading system logs', 'error')
        return render_template('admin/system_logs.html', logs=[])


@admin_required
def user_activity():
    """View user activity and login history"""
    try:
        # Get recent login activity from logs
        activities = []
        
        # Get all users with their last login info
        users = LoginInfo.query.all()
        for user in users:
            if user.profile:
                activities.append({
                    'user': user.username,
                    'name': user.profile.name,
                    'role': user.role,
                    'email': user.profile.gmail,
                    'status': 'Approved' if user.is_approved else 'Pending',
                    'last_activity': 'Recently Active'  # Could track this in future
                })
        
        # Get recent notifications for activity tracking
        recent_notifications = Notification.query.order_by(
            desc(Notification.created_at)
        ).limit(50).all()
        
        notification_activity = [{
            'user': notif.user.username if notif.user else 'System',
            'action': notif.description,
            'timestamp': notif.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_read': notif.is_read
        } for notif in recent_notifications]
        
        return render_template('admin/user_activity.html', 
                             users=activities,
                             notifications=notification_activity)
    except Exception as e:
        current_app.logger.error(f'Error loading user activity: {str(e)}')
        flash('Error loading user activity', 'error')
        return redirect(url_for('admin.admin_dashboard'))


@admin_required
def analytics():
    """System analytics and statistics"""
    try:
        # User statistics
        total_users = LoginInfo.query.count()
        active_users = LoginInfo.query.filter_by(is_approved=True).count()
        pending_users = LoginInfo.query.filter_by(is_approved=False).count()
        admins = LoginInfo.query.filter_by(role='admin').count()
        managers = LoginInfo.query.filter_by(role='manager').count()
        developers = LoginInfo.query.filter_by(role='developer').count()
        visitors = LoginInfo.query.filter_by(role='visitor').count()
        
        # Team statistics
        total_teams = Team.query.filter_by(is_deleted=False).count()
        teams_with_projects = db.session.query(Team.id).join(Project).distinct().count()
        
        # Project statistics
        total_projects = Project.query.filter_by(is_deleted=False).count()
        completed_projects = 0
        in_progress_projects = 0
        
        for project in Project.query.filter_by(is_deleted=False).all():
            total_tasks = len(project.tasks)
            if total_tasks > 0:
                completed_tasks = sum(1 for t in project.tasks if t.completion_status == CompletionStatus.completed)
                if completed_tasks == total_tasks:
                    completed_projects += 1
                else:
                    in_progress_projects += 1
        
        # Task statistics
        total_tasks = Task.query.filter_by(is_deleted=False).count()
        completed_tasks = Task.query.filter_by(
            is_deleted=False, 
            completion_status=CompletionStatus.completed
        ).count()
        in_progress_tasks = Task.query.filter_by(
            is_deleted=False,
            completion_status=CompletionStatus.in_progress
        ).count()
        todo_tasks = Task.query.filter_by(
            is_deleted=False,
            completion_status=CompletionStatus.to_do
        ).count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_notifications = Notification.query.filter(
            Notification.created_at >= week_ago
        ).count()
        
        stats = {
            'users': {
                'total': total_users,
                'active': active_users,
                'pending': pending_users,
                'admins': admins,
                'managers': managers,
                'developers': developers,
                'visitors': visitors
            },
            'teams': {
                'total': total_teams,
                'with_projects': teams_with_projects,
                'without_projects': total_teams - teams_with_projects
            },
            'projects': {
                'total': total_projects,
                'completed': completed_projects,
                'in_progress': in_progress_projects
            },
            'tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'in_progress': in_progress_tasks,
                'todo': todo_tasks,
                'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
            },
            'activity': {
                'notifications_week': recent_notifications
            }
        }
        
        return render_template('admin/analytics.html', stats=stats)
    except Exception as e:
        current_app.logger.error(f'Error loading analytics: {str(e)}')
        flash('Error loading analytics', 'error')
        return redirect(url_for('admin.admin_dashboard'))

