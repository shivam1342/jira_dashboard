from flask import request, redirect, url_for, render_template, session, flash, current_app
from models.login_info import LoginInfo, UserRole
from models.user_profile import UserProfile
from models.team_member import TeamMember, TeamRole
from models.team import Team
from models import db
from flask_mailman import EmailMessage
import random
import bcrypt
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


def signup_page():
    teams = Team.query.filter_by(is_deleted=False).all()
    return render_template('auth/register.html', teams=teams)


def signup():
    try:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        name = request.form.get('name', '').strip()
        gmail = request.form.get('gmail', '').strip()
        phone = request.form.get('phone', '').strip()
        gender = request.form.get('gender')
        team_id = request.form.get('team_id')

        # Validation
        if not all([username, password, name, gmail, phone]):
            flash('All fields are required', 'error')
            return redirect(url_for('auth.signup_page'))

        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('auth.signup_page'))

        # Check for existing username
        if LoginInfo.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            current_app.logger.warning(f'Signup attempt with existing username: {username}')
            return redirect(url_for('auth.signup_page'))

        # Check for existing email
        if UserProfile.query.filter_by(gmail=gmail).first():
            flash('Email already registered', 'error')
            current_app.logger.warning(f'Signup attempt with existing email: {gmail}')
            return redirect(url_for('auth.signup_page'))

        role = UserRole.developer if team_id else UserRole.visitor

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        login_info = LoginInfo(username=username, password=hashed_password, role=role)
        db.session.add(login_info)
        db.session.flush()  # Get the ID without committing

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
        
        current_app.logger.info(f'New user signup: {username} (email: {gmail}, role: {role.value})')
        flash('Signup successful. Please login after admin approval.', 'success')
        return redirect(url_for('auth.login_page'))

    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f'Database integrity error during signup: {str(e)}')
        flash('Error creating account. Username or email may already exist.', 'error')
        return redirect(url_for('auth.signup_page'))
    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(f'ValueError during signup: {str(e)}')
        flash('Invalid data provided. Please check your inputs.', 'error')
        return redirect(url_for('auth.signup_page'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Unexpected error during signup: {str(e)}', exc_info=True)
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('auth.signup_page'))


def login_page():
    return render_template('auth/login.html')


def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            if not username or not password:
                flash("Please enter both username and password.", "error")
                return redirect(url_for('auth.login_page'))

            user = LoginInfo.query.filter_by(username=username, is_deleted=False).first()

            if not user:
                current_app.logger.warning(f'Failed login attempt: username not found - {username}')
                flash("Invalid credentials.", "error")
                return redirect(url_for('auth.login_page'))

            # Verify password using bcrypt
            try:
                if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    current_app.logger.warning(f'Failed login attempt: wrong password - {username}')
                    flash("Invalid credentials.", "error")
                    return redirect(url_for('auth.login_page'))
            except Exception as bcrypt_error:
                current_app.logger.error(f'Bcrypt error for user {username}: {str(bcrypt_error)}')
                flash("Invalid credentials.", "error")
                return redirect(url_for('auth.login_page'))

            if not user.is_approved:
                current_app.logger.info(f'Login attempt by unapproved user: {username}')
                flash("Your account is pending admin approval.", "warning")
                return redirect(url_for('auth.login_page'))

            # Successful login
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role.value
            
            current_app.logger.info(f'Successful login: {username} (role: {user.role.value}) from IP: {request.remote_addr}')

            # Redirect based on role
            if user.role in [UserRole.developer, UserRole.manager]:
                return redirect(url_for('developer.developer_dashboard'))
            elif user.role == UserRole.admin:
                return redirect(url_for('admin.admin_dashboard'))
            elif user.role == UserRole.visitor:
                return redirect(url_for('visitor.view_approved_projects'))
            else:
                flash("Unsupported role.", "error")
                return redirect(url_for('auth.login_page'))

        except Exception as e:
            current_app.logger.error(f'Unexpected error during login: {str(e)}', exc_info=True)
            flash("An error occurred during login. Please try again.", "error")
            return redirect(url_for('auth.login_page'))

    return render_template('auth/login.html')


def forgot_password():
    # Handle GET and POST: POST triggers sending an OTP to the user's email
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please provide an email address.', 'error')
            return redirect(url_for('auth.forgot_password'))

        profile = UserProfile.query.filter_by(gmail=email).first()
        if not profile:
            flash('Email not found.', 'error')
            return redirect(url_for('auth.forgot_password'))

        login_info = LoginInfo.query.get(profile.login_info_id)
        if not login_info:
            flash('Associated login not found.', 'error')
            return redirect(url_for('auth.forgot_password'))

        # generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))
        session['reset_otp'] = otp
        session['reset_user_id'] = login_info.id

        # send OTP via email
        try:
            msg = EmailMessage(
                subject='Password reset OTP',
                body=f'Your password reset OTP is: {otp}',
                to=[email],
            )
            msg.send()
            flash('OTP sent to your email. Check inbox/spam.', 'success')
        except Exception as e:
            flash('Failed to send OTP email: ' + str(e), 'error')
            return redirect(url_for('auth.forgot_password'))

        return redirect(url_for('auth.verify_otp'))

    return render_template("auth/forgot_password.html")


def verify_otp():
    # Allows user to verify OTP and reset their password
    if request.method == 'POST':
        otp = request.form.get('otp')
        new_password = request.form.get('new_password')

        if not otp or not new_password:
            flash('Please provide OTP and new password.', 'error')
            return redirect(url_for('auth.verify_otp'))

        if 'reset_otp' not in session or 'reset_user_id' not in session:
            flash('Reset session expired. Please try again.', 'error')
            return redirect(url_for('auth.forgot_password'))

        if otp != session.get('reset_otp'):
            flash('Invalid OTP.', 'error')
            return redirect(url_for('auth.verify_otp'))

        user = LoginInfo.query.get(session.get('reset_user_id'))
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.forgot_password'))

        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        # clear reset session keys
        session.pop('reset_otp', None)
        session.pop('reset_user_id', None)

        flash('Password updated. Please login with your new password.', 'success')
        return redirect(url_for('auth.login_page'))

    return render_template('auth/forgot_password_verify.html')


def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('auth.login_page'))
