from flask import render_template, flash, redirect, url_for, request, make_response
from app import app, db
from app.forms import LoginForm, AddActivityForm, AddActivityTypeForm, ImportActivityForm, RegisterForm
from app.models import User, Activity, ActivityType
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from io import StringIO
import csv
from datetime import datetime


@app.route('/index')
@app.route('/')
@login_required
def index():
    activities = current_user.user_activities_grouped_by_date(request.args.get('hidensfw') is None)
    totals = current_user.user_activities_totals(request.args.get('hidensfw') is None)
    return render_template('index.html', activities=activities, totals=totals)


@app.route('/activity/add', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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
@app.route('/activity/import', methods=['GET', 'POST'])
@login_required
def importactivity():
    form = ImportActivityForm()
    if request.method == "POST":
        if form.validate_on_submit():
            f = request.files['file']
            fstring = f.read().decode("utf-8")
            csv_dicts = [{k: v for k, v in row.items()} for row in csv.DictReader(fstring.splitlines(), skipinitialspace=True)]
            _imported = 0;
            for r in csv_dicts:
                a_t = ActivityType.query.filter(ActivityType.name == r['activity']).first()
                if a_t is not None:
                    a = Activity(activitytype_id = a_t.id, user_id=current_user.id, timestamp=datetime.strptime(r['date'],"%Y-%m-%d"))
                    db.session.add(a)
                    db.session.commit()
                    _imported += 1;
                else:
                    flash('Activity Type {} does not exists. Not importing.'.format(r['activity']))
            flash('Imported {} activities.'.format(_imported))
        else:
            flash('Failed to add activity type.')
    return render_template('import.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if User.query.count() == 0:
        form = RegisterForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Successfully registered, you can now sign in.')
            return redirect(url_for('index'))
        return render_template('register.html', title="Register", form=form)
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
