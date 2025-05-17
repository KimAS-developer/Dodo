from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from dev.extensions import db
from domain.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth', methods=['GET', 'POST'])
def auth_handler():
    if current_user.is_authenticated:
        if current_user.is_cook():
            return redirect(url_for('orders.list_orders'))
        return redirect(url_for('mainPage.index'))

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'signup':
            return handle_signup(request)
        elif form_type == 'login':
            email = request.form.get('email')
            password = request.form.get('password')
            return handle_login(email, password)

    return render_template('auth.html')


def handle_login(email, password):
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        flash('Неверно указан email или пароль', 'error')
        return redirect(url_for('auth.auth_handler'))

    login_user(user)

    if user.is_cook():
        return redirect(url_for('orders.list_orders'))
    return redirect(url_for('mainPage.index'))


def handle_signup(request):
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Проверка совпадения паролей
    if password != confirm_password:
        flash("Пароли не совпадают", 'error')
        return redirect(url_for('auth.auth_handler'))

    # Проверка существования пользователя
    if User.query.filter_by(email=email).first():
        flash('Пользователь с таким email уже зарегистрирован', 'error')
        return redirect(url_for('auth.auth_handler'))

    # Создание нового пользователя
    new_user = User(
        name=name,
        email=email,
        role='client'  # или 'cook' в зависимости от вашей логики
    )

    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    flash('Пользователь успешно зарегистрирован', 'success')
    return redirect(url_for('auth.auth_handler'))


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.auth_handler'))