from flask import render_template, flash, redirect, url_for, request, make_response
from app import app, db
from app.forms import LoginForm, EditActivityForm, AddActivityForm, AddActivityTypeForm, ImportActivityForm, RegisterForm
from app.models import User, Activity, ActivityType
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from io import StringIO
import csv
import datetime


@app.route('/index')
@app.route('/')
@login_required
def index():
    plot_data = current_user.get_plot_data()
    totals = current_user.user_activities_totals(request.args.get('hidensfw') is None)
    monthnames = [datetime.date(1900, x, 1).strftime("%b") for x in range(1,13)]
    return render_template('index.html', plot_data=plot_data, totals=totals, monthnames=monthnames)

@app.route('/activity/list/<month>', methods=['GET'])
@login_required
def listactivities(month):
    month_list = current_user.activities_in_month(month)
    month_str = datetime.date(1900, int(month), 1).strftime("%B")
    return render_template('list.html', activities=month_list, month=month_str)

@app.route('/activity/edit/<activity_id>', methods=['GET', 'POST'])
@login_required
def editactivity(activity_id):
    activity = current_user.activities.filter(Activity.id == activity_id).first()
    if activity == None:
        flash('Not authorized to edit activity')
        return redirect(url_for('index'))
    else:
        form = EditActivityForm()
        form.activitytype.choices = [(type.id, type.name) for type in current_user.activitytypes]
        if request.method == 'GET':
            form.activitytype.default = activity.activitytype.id
            form.date.default = activity.timestamp
            form.process()
            return render_template('edit.html', form=form)
        else:
            if form.validate_on_submit():
                activity.timestamp = form.date.data
                activity.activitytype_id = form.activitytype.data
                db.session.commit()
                flash('Activity edited')
                return redirect(url_for('index'))


@app.route('/activity/delete/<activity_id>', methods=['GET'])
@login_required
def deleteactivity(activity_id):
    activity = current_user.activities.filter(Activity.id == activity_id).first()
    if activity == None:
        # not authorized or non existing
        flash('Not authorized to delete activity')
    else:
        db.session.delete(activity)
        db.session.commit()
        flash('Activity deleted')
    return redirect(url_for('index'))


@app.route('/activity/add', methods=['GET', 'POST'])
@login_required
def addactivity():
    form = AddActivityForm()
    form.activitytype.choices = [(type.id, type.name) for type in current_user.activitytypes]
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
            a_t = ActivityType(name=form.name.data, nsfw=form.nsfw.data is not None, user=current_user)
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
                a_t = current_user.activitytypes.filter(ActivityType.name == r['activity']).first()
                if a_t is None:
                    # TODO: Imports ActivityType as non NSFW make user choose
                    a_t = ActivityType(name=r['activity'],user_id=current_user.id)
                    db.session.add(a_t)
                    db.session.commit()
                a = Activity(activitytype_id = a_t.id, user_id=current_user.id, timestamp=datetime.datetime.strptime(r['date'],"%Y-%m-%d"))
                db.session.add(a)
                _imported += 1;
            db.session.commit()

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
