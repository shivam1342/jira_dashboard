from flask import request, redirect, url_for, render_template, flash, session
from models import db
from models.team import Team
from models.login_info import LoginInfo, UserRole
from models.user_profile import UserProfile
from models.project import Project
from models.team_member import TeamMember, TeamRole
from .decorators import admin_required
from flask_mailman import EmailMessage

@admin_required
def create_team():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description')
        manager_id = request.form.get('manager_id')

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

        flash('Team created successfully!')
        return redirect(url_for('admin.admin_dashboard'))

    potential_managers = LoginInfo.query \
        .filter(LoginInfo.is_deleted == False) \
        .join(TeamMember) \
        .filter(TeamMember.role == TeamRole.developer) \
        .all()

    return render_template('admin/create_team.html', managers=potential_managers)

@admin_required
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)

    if request.method == 'POST':
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
    team = Team.query.get_or_404(team_id)
    team.is_deleted = True
    db.session.commit()
    flash('Team archived successfully!')
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
    user = LoginInfo.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()

    subject = "You are approved by admin"
    message = f"Hello {user.username},\n\nYour Account has been approved by the admin."
    email = EmailMessage(subject, message, to=[user.profile.gmail])
    email.send()
    flash("User approved successfully.")
    return redirect(url_for('admin.view_users'))

@admin_required
def edit_user(user_id):
    user = LoginInfo.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.role = UserRole(request.form['role'])
        db.session.commit()
        flash('User updated successfully!')
        return redirect(url_for('admin.view_users'))

    return render_template('admin/edit_user.html', user=user)

@admin_required
def delete_user(user_id):
    user = LoginInfo.query.get_or_404(user_id)
    user.is_deleted = True
    db.session.commit()
    flash('User soft-deleted.')
    return redirect(url_for('admin.view_users'))

@admin_required
def reset_password(user_id):
    if request.method == 'POST':
        new_password = request.form['password']
        user = LoginInfo.query.get_or_404(user_id)
        user.password = new_password
        db.session.commit()
        flash("Password reset successfully.")
        return redirect(url_for('admin.view_users'))

    return render_template('admin/reset_password.html', user_id=user_id)

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
    all_projects = Project.query.filter_by(is_deleted=False).all()

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
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        name = request.form['name']
        gmail = request.form.get('gmail')
        phone = request.form.get('phone')
        team_id = request.form.get('team_id')

        try:
            new_user = LoginInfo(
                username=username,
                password=password,
                role=UserRole(role),
                is_approved=True,
                is_deleted=False
            )
            db.session.add(new_user)
            db.session.flush()

            profile = UserProfile(
                user_id=new_user.id,
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
