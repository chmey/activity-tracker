from datetime import datetime, timedelta
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from collections import defaultdict


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    activities = db.relationship('Activity', backref='user', lazy='dynamic')
    activitytypes = db.relationship('ActivityType', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def latest_user_activities(self):
        return self.activities.order_by(db.desc(Activity.timestamp)).limit(5).all()

    def user_activities_grouped_by_date(self, nsfw=True):
        activities = self.activities.order_by(db.asc(Activity.timestamp)).all()
        grouped = defaultdict(dict)
        for t in ActivityType.query.all():
            if (not t.nsfw) or (nsfw):
                dates = defaultdict(int)
                for a in activities:
                    if a.activitytype.id == t.id:
                        dates[a.timestamp.date()] += 1
                grouped[t] = dates
        return grouped

    def user_activities_totals(self, nsfw=True):
        activities = self.activities_ordered_by_recent()
        grouped = defaultdict(int)
        for t in ActivityType.query.all():
            if (not t.nsfw) or (nsfw):
                grouped[t] = sum(a.activitytype.id == t.id for a in activities) # TODO: Can probably SQL this
        return grouped

    def activities_ordered_by_recent(self):
        return self.activities.order_by(db.desc(Activity.timestamp)).all()

    def activities_ordered_by_first(self):
        return self.activities.order_by(db.asc(Activity.timestamp)).all()

    def get_plot_data(self):
        a_types = [at for at in self.activitytypes.all()]
        all_activities = self.activities_ordered_by_first() # TODO CAN BE OPTIMIZED GROUPED BY DATE ALREADY TAKES IT SORTED

        grouped_activities = self.user_activities_grouped_by_date()

        if not all_activities:
            return {'x': None, 'y': None, 'z': None}

        # https://stackoverflow.com/questions/993358/creating-a-range-of-dates-in-python
        date_range = [(all_activities[0].timestamp + timedelta(days=x)).date() for x in range(0, (all_activities[-1].timestamp-all_activities[0].timestamp).days+1)]

        z = []
        for at in a_types:
            row = []
            for date in date_range:
                if grouped_activities[at][date] is not None:
                    row.append(grouped_activities[at][date])
                else:
                    row.append('0')
            z.append(row)

        return {'x': date_range, 'y': [at.name for at in a_types], 'z': z}

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
    activitytype = db.relationship('ActivityType', backref=db.backref('activity', lazy='dynamic'))
    def __repr__(self):
        return '<Activity {}>'.format(self.id)

class ActivityType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(64), index=True, unique=True)
    nsfw = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<ActivityType {}>'.format(self.name)
