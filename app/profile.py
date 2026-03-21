from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import User, Schedule
from datetime import datetime


profile = Blueprint('profile', __name__, template_folder='template', static_folder='static')

@profile.route('/profile')
@login_required
def user_profile():
    user = User.query.filter_by(id=current_user.id).first()
    if user is None:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('main.index'))
    user_ico = user.profile_pic if user.profile_pic else 'profile_img_placeholder.jpg'
    
    if current_user.is_trainer:
        trainees = current_user.trainees.all()
        return render_template('profile.html', user_ico=user_ico, trainees=trainees)
    else:
        schedules = Schedule.query.filter_by(trainee_id=current_user.id).all()
        return render_template('profile.html', user_ico=user_ico, schedules=schedules)

@profile.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.all()
    trainers = User.query.filter_by(is_trainer=True).all()
    return render_template('admin.html', users=users, trainers=trainers)

@profile.route('/admin/assign_trainer', methods=['POST'])
@login_required
def admin_assign_trainer():
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.index'))

    trainee_id = request.form.get('trainee_id')
    trainer_id = request.form.get('trainer_id')
    if not trainee_id or not trainer_id:
        flash('Нужно выбрать тренера и ученика', 'danger')
        return redirect(url_for('profile.admin'))

    trainee = User.query.get(int(trainee_id))
    trainer = User.query.get(int(trainer_id))
    if not trainee or not trainer:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('profile.admin'))

    if not trainer.is_trainer:
        flash('Выбранный пользователь не является тренером', 'danger')
        return redirect(url_for('profile.admin'))

    if trainee.id == trainer.id:
        flash('Нельзя назначить пользователя тренером самому себе', 'warning')
        return redirect(url_for('profile.admin'))

    if trainee in trainer.trainees:
        flash('Тренер уже назначен этому пользователю', 'info')
        return redirect(url_for('profile.admin'))

    trainer.trainees.append(trainee)
    db.session.commit()
    flash(f'Тренер {trainer.username} назначен пользователю {trainee.username}', 'success')
    return redirect(url_for('profile.admin'))


@profile.route('/admin/remove_trainer', methods=['POST'])
@login_required
def admin_remove_trainer():
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.index'))

    trainee_id = request.form.get('trainee_id')
    trainer_id = request.form.get('trainer_id')
    if not trainee_id or not trainer_id:
        flash('Нужно выбрать тренера и ученика', 'danger')
        return redirect(url_for('profile.admin'))

    trainee = User.query.get(int(trainee_id))
    trainer = User.query.get(int(trainer_id))
    if not trainee or not trainer:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('profile.admin'))

    if trainee in trainer.trainees:
        trainer.trainees.remove(trainee)
        db.session.commit()
        flash(f'Тренер {trainer.username} удалён у пользователя {trainee.username}', 'success')
    else:
        flash('У этого пользователя нет такого тренера', 'info')

    return redirect(url_for('profile.admin'))


@profile.route('/trainer')
@login_required
def trainer():
    if not current_user.is_trainer:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.index'))
    return render_template('trainer.html')

@profile.route('/admin/user/<int:user_id>/update', methods=['POST'])
@login_required
def admin_update_user(user_id):
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    user.is_admin = (request.form.get('is_admin') == 'yes')
    user.is_trainer = (request.form.get('is_trainer') == 'yes')
    if current_user.id == user.id and not user.is_admin:
        flash('Нельзя лишить себя прав администратора', 'warning')
        return redirect(url_for('profile.admin'))

    db.session.commit()
    flash(f'Пользователь {user.username} обновлён', 'success')
    return redirect(url_for('profile.admin'))

@profile.route('/trainer/add_schedule/<int:trainee_id>', methods=['GET', 'POST'])
@login_required
def add_schedule(trainee_id):
    if not current_user.is_trainer:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('profile.user_profile'))
    
    trainee = User.query.get_or_404(trainee_id)
    if trainee not in current_user.trainees:
        flash('Этот пользователь не ваш клиент', 'danger')
        return redirect(url_for('profile.user_profile'))
    
    if request.method == 'POST':
        day_of_week = request.form.get('day_of_week')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            flash('Неверный формат времени', 'danger')
            return redirect(request.url)
        
        schedule = Schedule(
            trainee_id=trainee_id,
            trainer_id=current_user.id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(schedule)
        db.session.commit()
        flash('Расписание добавлено', 'success')
        return redirect(url_for('profile.user_profile'))
    
    return render_template('add_schedule.html', trainee=trainee)

@profile.route('/trainer/edit_schedule/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
def edit_schedule(schedule_id):
    if not current_user.is_trainer:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('profile.user_profile'))
    
    schedule = Schedule.query.get_or_404(schedule_id)
    if schedule.trainer_id != current_user.id:
        flash('Это не ваше расписание', 'danger')
        return redirect(url_for('profile.user_profile'))
    
    if request.method == 'POST':
        day_of_week = request.form.get('day_of_week')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            flash('Неверный формат времени', 'danger')
            return redirect(request.url)
        
        schedule.day_of_week = day_of_week
        schedule.start_time = start_time
        schedule.end_time = end_time
        db.session.commit()
        flash('Расписание обновлено', 'success')
        return redirect(url_for('profile.user_profile'))
    
    return render_template('edit_schedule.html', schedule=schedule)

@profile.route('/trainer/delete_schedule/<int:schedule_id>', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    if not current_user.is_trainer:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('profile.user_profile'))
    
    schedule = Schedule.query.get_or_404(schedule_id)
    if schedule.trainer_id != current_user.id:
        flash('Это не ваше расписание', 'danger')
        return redirect(url_for('profile.user_profile'))
    
    db.session.delete(schedule)
    db.session.commit()
    flash('Расписание удалено', 'success')
    return redirect(url_for('profile.user_profile'))

@profile.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Нельзя удалить себя', 'warning')
        return redirect(url_for('profile.admin'))

    db.session.delete(user)
    db.session.commit()
    flash(f'Пользователь {user.username} удалён', 'success')
    return redirect(url_for('profile.admin'))
