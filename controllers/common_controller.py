from flask import request, render_template, flash, session, redirect, url_for, jsonify
from models import Project, Team, LoginInfo, Task, db
from models.user_profile import UserProfile
from models.note import Note, NoteType
from models.notification import Notification
from sqlalchemy import or_
from datetime import datetime

def handle_search():
    query = request.args.get('q', '').strip()

    if not query:
        flash("Enter a search query.")
        return render_template("partials/search_results.html", query=query)

    projects = Project.query.filter(Project.name.ilike(f"%{query}%")).all()
    teams = Team.query.filter(Team.name.ilike(f"%{query}%")).all()
    tasks = Task.query.filter(Task.task_name.ilike(f"%{query}%")).all()
    users = LoginInfo.query.filter(
        or_(
            LoginInfo.username.ilike(f"%{query}%"),
            # LoginInfo.email.ilike(f"%{query}%")
        )
    ).all()

    return render_template(
        "partials/search_results.html",
        query=query,
        projects=projects,
        teams=teams,
        tasks = tasks,
        users=users
    )


def view_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your profile.")
        return redirect(url_for('auth.login'))

    login_info = LoginInfo.query.get_or_404(user_id)
    profile = UserProfile.query.filter_by(login_info_id=user_id).first()

    return render_template("partials/profile.html", login_info=login_info, user_profile=profile)



def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("Login required.")
        return redirect(url_for('auth.login'))

    user = LoginInfo.query.get_or_404(user_id)
    profile = UserProfile.query.filter_by(login_info_id=user_id).first()


    if request.method == 'POST':
        profile.name = request.form.get('name', profile.name)
        profile.gmail = request.form.get('gmail', profile.gmail)
        profile.phone = request.form.get('phone', profile.phone)
        profile.gender = request.form.get('gender', profile.gender)

        db.session.commit()
        flash("Profile updated successfully.")
        return redirect(url_for('common.view_profile'))

    return render_template("partials/edit_profile.html", current_user=user, profile=profile)


# ==================== NOTES ====================

def create_note(task_id):
    """Create a note/query/issue on a task"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401

    task = Task.query.get_or_404(task_id)
    
    if request.method == 'POST':
        content = request.form.get('content')
        note_type = request.form.get('note_type', 'comment')
        parent_note_id = request.form.get('parent_note_id')

        if not content:
            flash('Note content is required.', 'error')
            return redirect(url_for('developer.view_task_details', task_id=task_id))

        note = Note(
            task_id=task_id,
            note_type=NoteType[note_type],
            content=content,
            text=content,  # keeping both for compatibility
            created_by=user_id,
            parent_note_id=int(parent_note_id) if parent_note_id else None,
            is_resolved=False,
            is_deleted=False
        )
        db.session.add(note)
        
        # Create notification if it's a query or issue
        if note_type in ['query', 'issue'] and task.manager_id:
            notification = Notification(
                user_id=task.manager_id,
                description=f"New {note_type} raised on task '{task.task_name}'",
                notification_type=f'{note_type}_raised',
                related_task_id=task_id,
                action_url=url_for('developer.view_task_details', task_id=task_id),
                is_read=False
            )
            db.session.add(notification)
        
        db.session.commit()
        flash(f'{note_type.capitalize()} added successfully.', 'success')
        return redirect(url_for('developer.view_task_details', task_id=task_id))


def edit_note(note_id):
    """Edit an existing note"""
    user_id = session.get('user_id')
    note = Note.query.get_or_404(note_id)
    
    if note.created_by != user_id:
        flash('You can only edit your own notes.', 'error')
        return redirect(url_for('developer.view_task_details', task_id=note.task_id))
    
    if request.method == 'POST':
        note.content = request.form.get('content', note.content)
        note.text = note.content
        note.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Note updated successfully.', 'success')
    
    return redirect(url_for('developer.view_task_details', task_id=note.task_id))


def delete_note(note_id):
    """Soft delete a note"""
    user_id = session.get('user_id')
    note = Note.query.get_or_404(note_id)
    
    if note.created_by != user_id:
        flash('You can only delete your own notes.', 'error')
        return redirect(url_for('developer.view_task_details', task_id=note.task_id))
    
    note.is_deleted = True
    db.session.commit()
    flash('Note deleted successfully.', 'success')
    return redirect(url_for('developer.view_task_details', task_id=note.task_id))


def resolve_note(note_id):
    """Mark a query/issue as resolved (manager only)"""
    user_id = session.get('user_id')
    note = Note.query.get_or_404(note_id)
    task = Task.query.get(note.task_id)
    
    if task.manager_id != user_id:
        flash('Only the task manager can resolve queries/issues.', 'error')
        return redirect(url_for('developer.view_task_details', task_id=note.task_id))
    
    note.is_resolved = True
    db.session.commit()
    
    # Notify the note creator
    notification = Notification(
        user_id=note.created_by,
        description=f"Your {note.note_type.value} on task '{task.task_name}' has been resolved",
        notification_type='query_resolved',
        related_task_id=task.id,
        action_url=url_for('developer.view_task_details', task_id=task.id),
        is_read=False
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Note marked as resolved.', 'success')
    return redirect(url_for('developer.view_task_details', task_id=note.task_id))


# ==================== NOTIFICATIONS ====================

def get_notifications():
    """Get all notifications for current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    notifications = Notification.query.filter_by(user_id=user_id, is_read=False)\
        .order_by(Notification.created_at.desc())\
        .limit(10)\
        .all()
    
    return render_template('partials/notifications_dropdown.html', notifications=notifications)


def get_all_notifications():
    """Get all notifications page"""
    user_id = session.get('user_id')
    if not user_id:
        flash('Login required.', 'error')
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('type', 'all')
    
    query = Notification.query.filter_by(user_id=user_id)
    
    if filter_type != 'all':
        query = query.filter_by(notification_type=filter_type)
    
    notifications = query.order_by(Notification.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('partials/all_notifications.html', notifications=notifications, filter_type=filter_type)


def mark_notification_read(notification_id):
    """Mark a notification as read"""
    user_id = session.get('user_id')
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})


def mark_all_notifications_read():
    """Mark all notifications as read"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    Notification.query.filter_by(user_id=user_id, is_read=False)\
        .update({'is_read': True})
    db.session.commit()
    
    return jsonify({'success': True})


def get_notification_count():
    """Get unread notification count for badge"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'count': 0})
    
    count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    return jsonify({'count': count})