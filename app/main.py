from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User

main = Blueprint('main', __name__, template_folder='template')

@main.route('/')
def index():
    return render_template('main.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            flash('Заполните все поля', 'danger')
            return redirect(url_for('main.register'))

        if User.query.filter((User.username == username)).first():
            flash('Пользователь уже существует', 'danger')
            return redirect(url_for('main.register'))

        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно, войдите', 'success')
        return redirect(url_for('main.index'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Вы успешно авторизованы', 'success')
            return redirect(url_for('main.index'))
        flash('Неверные учетные данные', 'danger')
        return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/ggbb', methods=['GET', 'POST'])
def ggbb():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        admin_status = request.form.get('status') == 'on'
        if not username or not password:
            flash('Заполните все поля', 'danger')
            return redirect(url_for('main.register'))

        if User.query.filter((User.username == username)).first():
            flash('Пользователь уже существует', 'danger')
            return redirect(url_for('main.register'))

        user = User(username=username, password=generate_password_hash(password), is_admin=admin_status)
        db.session.add(user)
        db.session.commit()
        flash('Пользователь успешно добавлен', 'success')
        return redirect(url_for('main.index'))
    return render_template('register.html', admin=True)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main.index'))
