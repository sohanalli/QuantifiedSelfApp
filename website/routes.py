from website import app,db
from website import charts
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt

from flask import render_template, request, flash, redirect, url_for
from website.models import User, Tracker, Log
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

@app.route("/")
@app.route("/home")
@login_required
def home_page():
    return render_template("home.html",user=current_user)

@app.route("/login", methods=['GET','POST'])
def login_page():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password_hash,password):
                flash("Logged In succesfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for('home_page'))
            else:
                flash("Incorrect Password, Try again!", category="error")
        else:
            flash("User does not exist!", category="error")
    return render_template("login.html",user=current_user)

@app.route("/signup", methods=['GET','POST'])
def signup_page():
    if request.method=='POST':
        email = request.form.get('email')
        name = request.form.get('name')
        contactnum = request.form.get('contactnum')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email ID already exists!", category="error")
        elif len(contactnum)!=10:
            flash("Enter a valid mobile number!", category="error")
        elif len(name) < 2:
            flash("Name must be greater than 1 character!", category="error")
        elif password1 != password2:
            flash("Passwords don\'t match!", category="error")
        elif len(password1) < 7:
            flash("Password must be at least 6 characters", category="error")
        else:
            user_to_create = User(name=name,email=email,contactnum=contactnum,password_hash=generate_password_hash(password1, method="sha256"))
            db.session.add(user_to_create)
            db.session.commit()
            flash("Account created!", category="success")
            login_user(user_to_create, remember=True)
            return redirect(url_for('home_page'))

    return render_template("signup.html",user=current_user)

@login_required
@app.route("/profile")
def profile_page():
    return render_template("profile.html",user=current_user)

@app.route("/about")
def about_page():
    return render_template("about.html",user=current_user)

@app.route("/logout")
@login_required
def logout_page():
    logout_user()
    flash('Logged out Successfully!',category="success")
    return redirect(url_for('login_page'))

@app.route("/view-trackers")
@login_required
def view_trackers_page():
    trackers = Tracker.query.filter_by(user_id=current_user.id)
    return render_template("view_trackers.html", user=current_user,trackers=trackers)

@app.route("/add-tracker", methods=['GET','POST'])
@login_required
def add_tracker_page():
    if request.method=='POST':
        name = request.form.get('name')
        description = request.form.get('description')
        settings = request.form.get('settings')
        tracker_type = request.form.get('tracker_type')

        tracker = Tracker.query.filter_by(name=name).first()
        if tracker:
            flash("Tracker already exists!", category="error")
        tracker_to_create = Tracker(name=name, description=description, settings=settings, tracker_type=tracker_type, user_id=current_user.id)
        db.session.add(tracker_to_create)
        db.session.commit()
        flash(name + " tracker added!", category="success")
        return redirect(url_for('view_trackers_page'))
    return render_template("add_tracker.html", user=current_user)

@app.route("/edit-profile",methods=['GET','POST'])
@login_required
def edit_profile_page():
    if request.method=='POST':
        name = request.form.get('name')
        contactnum = request.form.get('contactnum')

        if len(contactnum)!=10:
            flash("Enter a valid mobile number!", category="error")
        elif len(name) < 2:
            flash("Name must be greater than 1 character!", category="error")
        else:
            user=User.query.get(current_user.id)
            user.name = request.form.get('name')
            user.contactnum = request.form.get('contactnum')
            db.session.commit()
            flash("Account Updated!", category="success")
            return redirect(url_for('profile_page'))
    return render_template("edit_profile.html", user=current_user)

@app.route("/delete-tracker/<int:record_id>",methods=['GET','POST'])
@login_required
def delete_tracker_page(record_id):
    try:
        tracker = Tracker.query.get(record_id)
        logs = Log.query.all()
        tracker_name = tracker.name
        db.session.delete(tracker)
        for log in logs:
            if log.tracker_id==record_id and log.user_id==current_user.id:
                db.session.delete(log)
        db.session.commit()
        flash(tracker_name + " tracker removed succesfully!", category="success")
    except Exception as e:
        print(e)
        flash('Something went wrong.', category='error')
    return redirect(url_for('view_trackers_page'))

@app.route("/edit-tracker/<int:record_id>",methods=['GET','POST'])
@login_required
def edit_tracker_page(record_id):
    tracker = Tracker.query.get(record_id)
    if request.method=='POST':
        tracker.name = request.form.get('name')
        tracker.description = request.form.get('description')
        tracker.settings = request.form.get('settings')
        tracker.tracker_type = request.form.get('tracker_type')
        
        db.session.commit()
        flash(tracker.name + " tracker edited!", category="success")
        return redirect(url_for('view_trackers_page'))
    return render_template('edit_tracker.html',tracker=tracker,user=current_user)

@app.route("/add-log/<int:record_id>",methods=['GET','POST'])
@login_required
def add_log_page(record_id):
    tracker = Tracker.query.get(record_id)
    import datetime
    now = datetime.datetime.now()
    try:
        if request.method=='POST':
            timestamp = request.form.get('timestamp')
            value = request.form.get('value')
            notes = request.form.get('notes')
            log_to_create = Log(timestamp=timestamp,value=value,notes=notes,tracker_id=record_id,user_id=current_user.id,added_date_time=now)
            db.session.add(log_to_create)
            db.session.commit()
            flash('New Log added for ' + tracker.name + ' tracker ', category="success")
            return redirect(url_for('view_trackers_page'))
    except Exception as e:
        print(e)
        flash('Something went wrong.', category='error')
    return render_template('add_log.html',tracker=tracker,user=current_user)

@app.route("/view-logs/<int:record_id>")
@login_required
def view_logs_page(record_id):
    tracker = Tracker.query.get(record_id)
    logs = Log.query.all()
    import sqlite3
    con = sqlite3.connect('database.db')
    # print("Database opened successfully")
    c = con.cursor()
    c.execute('SELECT timestamp, value FROM log WHERE user_id={} AND tracker_id={}'.format(current_user.id,record_id))
    data = c.fetchall()

    dict = {}
    
    from matplotlib import style
    style.use('fivethirtyeight')

    from dateutil import parser

    for row in data:
        dict[parser.parse(row[0])]=row[1]
    from collections import OrderedDict

    fig = plt.figure(figsize=(18, 8))
    dict = OrderedDict(sorted(dict.items()))
    if tracker.settings=='mood' or tracker.tracker_type=="Boolean":
        plt.scatter(dict.keys(), dict.values(), s=500)
    else:
        plt.plot_date(dict.keys(), dict.values(), '-')
    plt.xlabel('Date')
    plt.ylabel('Values')
    plt.tight_layout()
    plt.savefig('static/images/graph.png')
    return render_template('view_logs.html',tracker=tracker,user=current_user,logs=logs)

@app.route("/delete-log/<int:record_id>")
@login_required
def delete_log_page(record_id):
    try:
        logs = Log.query.all()
        for log in logs:
            if log.id==record_id:
                db.session.delete(log)
                db.session.commit()
                flash("Log deleted succesfully!", category="success")
    except Exception as e:
        print(e)
        flash('Something went wrong.', category='error')
    return redirect(url_for('view_trackers_page'))

@app.route("/edit-log/<int:record_id>",methods=['GET','POST'])
@login_required
def edit_log_page(record_id):
    log = Log.query.get(record_id)
    tracker_id = log.tracker_id
    tracker = Tracker.query.get(tracker_id)
    if request.method=='POST':
        log.timestamp = request.form.get('timestamp')
        log.value = request.form.get('value')
        log.notes = request.form.get('notes')
        
        db.session.commit()
        flash(" log edited!", category="success")
        return redirect(url_for('view_logs_page',record_id=tracker.id))
    return render_template('edit_log.html',log=log,user=current_user,tracker=tracker)