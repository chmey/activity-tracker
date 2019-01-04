from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    activities = db.relationship('Activity', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    activitytype_id = db.Column(db.Integer, db.ForeignKey('activity_type.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    activitytype = db.relationship('ActivityType', backref='activity', lazy=False)

    def __repr__(self):
        return '<Activity {} by {}>'.format(self.id, self.user_id)

class ActivityType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    nsfw = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<ActivityType {}>'.format(self.name)
