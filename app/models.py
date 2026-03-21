from . import db
from flask_login import UserMixin

trainer_assignment = db.Table(
    'trainer_assignment',
    db.Column('trainer_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('trainee_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_pic = db.Column(db.String(255), nullable=True)
    is_trainer = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    trainees = db.relationship(
        'User', secondary=trainer_assignment,
        primaryjoin=(trainer_assignment.c.trainer_id == id),
        secondaryjoin=(trainer_assignment.c.trainee_id == id),
        backref=db.backref('trainers', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<User {self.username}>'

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trainee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)  # e.g., 'Monday'
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    trainee = db.relationship('User', foreign_keys=[trainee_id], backref='schedules')
    trainer = db.relationship('User', foreign_keys=[trainer_id])

    def __repr__(self):
        return f'<Schedule {self.trainee.username} {self.day_of_week} {self.start_time}-{self.end_time}>'
