import re

from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_required, current_user

from dev import db

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    if request.method == 'POST':
        # Обновление данных
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')

        # Проверка и обновление пароля
        new_password = request.form.get('new_password')
        if new_password:
            if len(new_password) < 6:
                flash('Пароль должен содержать не менее 6 символов', 'error')
                return redirect(url_for('profile.view_profile'))

            # Проверка на наличие и цифр, и букв
            if not (re.search(r'\d', new_password) and re.search(r'[a-zA-Z]', new_password)):
                flash('Пароль должен содержать как буквы, так и цифры', 'error')
                return redirect(url_for('profile.view_profile'))

            current_user.password = new_password  # Сохраняем пароль без хеширования

        try:
            db.session.commit()
            flash('Данные успешно обновлены', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении данных: {str(e)}', 'error')

        return redirect(url_for('profile.view_profile'))

    return render_template('profile.html', user=current_user)