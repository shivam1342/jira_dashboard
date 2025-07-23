from flask import request, render_template, flash, session, redirect, url_for
from models import Project, Team, LoginInfo, Task, db
from models.user_profile import UserProfile
from sqlalchemy import or_

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