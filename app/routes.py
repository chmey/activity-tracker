from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, AddActivityForm
from app.models import User, Activity, ActivityType
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
@login_required
def index():
    activities = current_user.activities
    if request.args.get('hideNSFW') is not None:
        activities = [a for a in activities if not a.activitytype.nsfw == True]

    return render_template('index.html', activities=activities)


@app.route('/add', methods=['GET', 'POST'])
def addactivity():
    form = AddActivityForm()
    form.activitytype.choices = [(type.id, type.name) for type in ActivityType.query.all()]
    if form.validate_on_submit():
        a = Activity(activitytype_id = form.activitytype.data, user_id=current_user.id, timestamp=form.date.data)
        db.session.add(a)
        db.session.commit()
        flash('Activity added!')
        return redirect(url_for('index'))
    else:
        flash('Failed to add activity')
    return render_template('add.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title="Sign In", form=form)

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
