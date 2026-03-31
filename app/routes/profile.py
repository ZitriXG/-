from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from app import db
from app.models import User

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/')
@login_required
def index():
    return render_template('profile/index.html')


@profile_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('profile/settings.html', active_tab='profile')


@profile_bp.route('/settings/profile', methods=['POST'])
@login_required
def update_profile():
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    bio = request.form.get('bio', '').strip()
    phone = request.form.get('phone', '').strip()
    birth_date_str = request.form.get('birth_date', '').strip()
    profile_public = request.form.get('profile_public') == 'on'

    birth_date = None
    if birth_date_str:
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Неверный формат даты рождения.', 'danger')
            return redirect(url_for('profile.settings'))

    current_user.first_name = first_name or None
    current_user.last_name = last_name or None
    current_user.bio = bio or None
    current_user.phone = phone or None
    current_user.birth_date = birth_date
    current_user.profile_public = profile_public

    db.session.commit()
    flash('Профиль обновлён.', 'success')
    return redirect(url_for('profile.settings') + '#profile')


@profile_bp.route('/settings/account', methods=['POST'])
@login_required
def update_account():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip().lower()

    error = None
    if not username or len(username) < 3:
        error = 'Имя пользователя должно содержать не менее 3 символов.'
    elif not email or '@' not in email:
        error = 'Введите корректный email.'
    elif username != current_user.username and User.query.filter_by(username=username).first():
        error = 'Это имя пользователя уже занято.'
    elif email != current_user.email and User.query.filter_by(email=email).first():
        error = 'Этот email уже зарегистрирован.'

    if error:
        flash(error, 'danger')
    else:
        current_user.username = username
        current_user.email = email
        db.session.commit()
        flash('Данные аккаунта обновлены.', 'success')

    return redirect(url_for('profile.settings') + '#account')


@profile_bp.route('/settings/password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not current_user.check_password(current_password):
        flash('Текущий пароль введён неверно.', 'danger')
    elif len(new_password) < 6:
        flash('Новый пароль должен содержать не менее 6 символов.', 'danger')
    elif new_password != confirm_password:
        flash('Новые пароли не совпадают.', 'danger')
    else:
        current_user.set_password(new_password)
        db.session.commit()
        flash('Пароль успешно изменён.', 'success')

    return redirect(url_for('profile.settings') + '#password')


@profile_bp.route('/settings/notifications', methods=['POST'])
@login_required
def update_notifications():
    email_notifications = request.form.get('email_notifications') == 'on'
    current_user.email_notifications = email_notifications
    db.session.commit()
    flash('Настройки уведомлений сохранены.', 'success')
    return redirect(url_for('profile.settings') + '#notifications')


@profile_bp.route('/settings/delete', methods=['POST'])
@login_required
def delete_account():
    password = request.form.get('password', '')
    if not current_user.check_password(password):
        flash('Неверный пароль. Аккаунт не удалён.', 'danger')
        return redirect(url_for('profile.settings') + '#danger')

    from flask_login import logout_user
    user = current_user._get_current_object()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('Аккаунт удалён.', 'info')
    return redirect(url_for('main.index'))
