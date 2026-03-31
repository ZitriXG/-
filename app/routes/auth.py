from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        error = None
        if not username or len(username) < 3:
            error = 'Имя пользователя должно содержать не менее 3 символов.'
        elif not email or '@' not in email:
            error = 'Введите корректный email.'
        elif len(password) < 6:
            error = 'Пароль должен содержать не менее 6 символов.'
        elif password != confirm_password:
            error = 'Пароли не совпадают.'
        elif User.query.filter_by(username=username).first():
            error = 'Это имя пользователя уже занято.'
        elif User.query.filter_by(email=email).first():
            error = 'Этот email уже зарегистрирован.'

        if error:
            flash(error, 'danger')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('profile.settings'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        login_input = request.form.get('login', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter(
            (User.email == login_input.lower()) | (User.username == login_input)
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Добро пожаловать, {user.get_full_name()}!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Неверные данные для входа.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('main.index'))
