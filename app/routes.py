from flask import render_template, flash, redirect, url_for, request, make_response
from app import app, db
from app.forms import LoginForm, AddActivityForm, AddActivityTypeForm
from app.models import User, Activity, ActivityType
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from io import StringIO
import csv


@app.route('/index')
@app.route('/')
@login_required
def index():
    activities = current_user.user_activities_grouped_by_date(request.args.get('hidensfw') is None)
    totals = current_user.user_activities_totals(request.args.get('hidensfw') is None)
    return render_template('index.html', activities=activities, totals=totals)


@app.route('/activity/add', methods=['GET', 'POST'])
def addactivity():
    form = AddActivityForm()
    form.activitytype.choices = [(type.id, type.name) for type in ActivityType.query.all()]
    if request.method == "POST":
        if form.validate_on_submit():
            a = Activity(activitytype_id = form.activitytype.data, user_id=current_user.id, timestamp=form.date.data)
            db.session.add(a)
            db.session.commit()
            flash('Activity added!')
            return redirect(url_for('index'))
        else:
            flash('Failed to add activity.')
    return render_template('add.html', form=form, what="Activity")

@app.route('/activitytype/add', methods=['GET', 'POST'])
def addactivitytype():
    form = AddActivityTypeForm()
    if request.method == "POST":
        if form.validate_on_submit():
            a_t = ActivityType(name = form.name.data, nsfw = form.nsfw.data is not None)
            db.session.add(a_t)
            db.session.commit()
            flash('Activity Type added!')
            return redirect(url_for('index'))
        else:
            flash('Failed to add activity type.')
    return render_template('add.html', form=form, what="Activity Type")

@app.route('/activity/export')
def exportactivity():
    activities = current_user.activities_ordered_by_first()
    si = StringIO()
    cw = csv.DictWriter(si, fieldnames=['activity','date'])
    cw.writeheader()
    for a in activities:
        cw.writerow({'activity': a.activitytype.name,'date':a.timestamp.date()})
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

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
