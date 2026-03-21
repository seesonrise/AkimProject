from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import User


profile = Blueprint('profile', __name__, template_folder='template', static_folder='static')

@profile.route('/profile')
@login_required
def user_profile():
    user = User.query.filter_by(id=current_user.id).first()
    if user is None:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('main.index'))
    user_ico = user.profile_pic if user.profile_pic else 'profile_img_placeholder.jpg'
    return render_template('profile.html', user_ico=user_ico)

@profile.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.index'))
    return render_template('admin.html')

@profile.route('/trainer')
@login_required
def trainer():
    if not current_user.is_trainer:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.index'))
    return render_template('trainer.html')
