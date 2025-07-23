from flask import request, redirect, url_for, render_template, session, flash
from models.login_info import LoginInfo, UserRole
from models.user_profile import UserProfile
from models.team_member import TeamMember, TeamRole
from models.team import Team
from models import db


def signup_page():
    teams = Team.query.filter_by(is_deleted=False).all()
    return render_template('auth/register.html', teams=teams)


def signup():
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    gmail = request.form['gmail']
    phone = request.form['phone']
    gender = request.form['gender']
    team_id = request.form.get('team_id')

    if LoginInfo.query.filter_by(username=username).first():
        flash('Username already exists', 'error')
        return redirect(url_for('auth.signup_page'))

    if UserProfile.query.filter_by(gmail=gmail).first():
        flash('Email already registered', 'error')
        return redirect(url_for('auth.signup_page'))

    role = UserRole.developer if team_id else UserRole.visitor

    login_info = LoginInfo(username=username, password=password, role=role)
    db.session.add(login_info)
    db.session.commit()

    user_profile = UserProfile(
        login_info_id=login_info.id,
        name=name,
        gmail=gmail,
        phone=phone,
        gender=gender
    )
    db.session.add(user_profile)

    if team_id:
        team_member = TeamMember(
            user_id=login_info.id,
            team_id=int(team_id),
            role=TeamRole.developer
        )
        db.session.add(team_member)

    db.session.commit()

    flash('Signup successful. Please login after admin approval.', 'success')
    return redirect(url_for('auth.login_page'))


def login_page():
    return render_template('auth/login.html')


def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = LoginInfo.query.filter_by(username=username, password=password, is_deleted=False).first()

        if not user:
            flash("Invalid credentials.", "error")
            return redirect(url_for('auth.login_page'))

        if not user.is_approved:
            flash("Your account is pending admin approval.", "error")
            return redirect(url_for('auth.login_page'))

        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role.value
        
        print("Logged in user ID:", user.id)


        if user.role in [UserRole.developer, UserRole.manager]:
            return redirect(url_for('developer.developer_dashboard'))
        elif user.role == UserRole.admin:
            return redirect(url_for('admin.admin_dashboard'))
        elif user.role == UserRole.visitor:
            return redirect(url_for('visitor.view_approved_projects'))
        else:
            flash("Unsupported role.", "error")

        return redirect(url_for('auth.login_page'))

    return render_template('auth/login.html')


def forgot_password():
    return render_template("auth/forgot_password.html")


def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('auth.login_page'))
