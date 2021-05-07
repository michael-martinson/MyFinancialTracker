from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    logging,
    session,
    g,
    Response,
) 
import sqlite3
import json
from markupsafe import escape
import secrets
import os
import datetime, calendar
from db import (DB, BadRequest, KeyNotFound, UsernameAlreadyExists)

# Configure application
app = Flask(__name__)
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

# path to database
DATABASE = './myfinancials.db'

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = 'f4_LpwUFVA2WaLjsjcwrgS8WrFt4pmAa4A' 

########################################
## login endpoints                    ##
########################################

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] and request.form['password']:
            db = DB(get_db())
            try:
                if db.validate_user(request):
                    session['username'] = request.form['username']
                else:
                    error = 'Invalid Credentials. Please try again.'
                    return render_template('login.html', newuser=False, error=error)
            except Exception as e:
                app.logger.error(e)
                error = 'Invalid Credentials. Please try again.'
                return render_template('login.html', newuser=False, error=error)
            return redirect(url_for('myexpenses'))
        else:
            error = 'Username or Password was empty. Please try again.'
    return render_template('login.html', newuser=False, error=error)

@app.route("/newuser", methods=["GET", "POST"])
def createuser():
    error = None
    if request.method == 'POST':
        db = DB(get_db())
        try:
            db.add_user(request)
            session['username'] = request.form['username']
        except UsernameAlreadyExists as e:
            app.logger.error(e.message)
            error = "Username already exists. Try a different one."
            return render_template('login.html', newuser=True, error=error)
        except Exception as e:
            app.logger.error(e)
            return render_template('login.html', newuser=True, error=e)
        return redirect(url_for('myexpenses'))
    return render_template('login.html', newuser=True, error=error)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('login'))


########################################
## Expense endpoints                  ##
########################################

@app.route('/addexpense', methods=['POST'])
def addexpense():
    if not check_logged_in():
        return redirect(url_for('login'))
    db = DB(get_db())
    message = "Expense added successfully"
    try:
        db.addexpense(session['username'], request)
    except BadRequest as e:
        app.logger.error(f"{e}")
        message = "Add expense failed. Make user form input is correct"
    return redirect(url_for('myexpenses'))

@app.route("/")
@app.route("/myexpenses/")
@app.route('/myexpenses/<target_date>', methods=['Get'])
def myexpenses(target_date = None):
    if not check_logged_in():
        return redirect(url_for('login'))
    db = DB(get_db())
    message = None
    myexpenses = None
    etot = None
    stot = None
    if not target_date:
        target_date = datetime.date.today()
    else:
        target_date = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
    try:
        (myexpenses,etot,stot) = db.myexpenses(session['username'], target_date)
        print(myexpenses, etot, stot)
    except BadRequest as e:
        app.logger.error(f"{e}")
        message = "Something went wrong. Please try again"
    return render_template(
        "myexpenses.html", 
        rows=myexpenses,
        etotal=etot,
        stotal=stot,
        month=calendar.month_name[target_date.month],
        year=target_date.year,
        table="expenses",
        message=message,
        username=session['username']
    ) 

########################################
## Spending endpoints                 ##
########################################

@app.route('/addspending', methods=['POST'])
def addspending():
    if not check_logged_in():
        return redirect(url_for('login'))
    db = DB(get_db())
    message = "Spending added successfully"
    try:
        db.addspending(session['username'], request)
    except BadRequest as e:
        app.logger.error(f"{e}")
        message = "Add spending failed. Make user form input is correct"
    return redirect(url_for('myspending'))

@app.route('/myspending/', methods=['Get'])
@app.route('/myspending/<target_date>', methods=['Get'])
def myspending(target_date = None):
    if not check_logged_in():
        return redirect(url_for('login'))
    db = DB(get_db())
    message = None
    myspending = None
    if not target_date:
        target_date = datetime.date.today()
    else:
        target_date = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
    try:
        (myspending, total) = db.myspending(session['username'], target_date)
        print(myspending)
    except BadRequest as e:
        app.logger.error(f"{e}")
        message = "Something went wrong. Please try again"
    return render_template(
        "myspending.html", 
        rows=myspending, 
        total=total, 
        month=calendar.month_name[target_date.month],
        year=target_date.year,
        table="spending", 
        message=message, 
        username=session['username']
    ) 


########################################
## Goal endpoints                     ##
########################################

@app.route('/addgoal', methods=['POST'])
def addgoal():
    if not check_logged_in():
        return redirect(url_for('login'))
    db = DB(get_db())
    message = "goal added successfully"
    try:
        db.addgoal(session['username'], request)
    except BadRequest as e:
        app.logger.error(f"{e}")
        message = "Add goal failed. Make user form input is correct"
    return redirect(url_for('mygoals'))

@app.route('/mygoals/', methods=['Get'])
def mygoals():
    if not check_logged_in():
        return redirect(url_for('login'))
    db = DB(get_db())
    message = None
    mygoals = None
    try:
        (mygoals, total) = db.mygoals(session['username'])
        print(mygoals)
    except BadRequest as e:
        app.logger.error(f"{e}")
        message = "Something went wrong. Please try again"
    return render_template(
        "mygoals.html", 
        rows=mygoals,
        total=total, 
        table="goals",
        message=message,
        username=session['username']
    ) 


########################################
## Debt endpoints                     ##
########################################

@app.route('/adddebt', methods=['POST'])
def adddebt():
    if not check_logged_in():
        return redirect(url_for('login'))
    db = DB(get_db())
    message = "Debt added successfully"
    try:
        db.adddebt(session['username'], request)
    except BadRequest as e:
        app.logger.error(f"{e}")
        message = "Add Debt failed. Make user form input is correct"
    return redirect(url_for('mydebt'))

@app.route('/mydebt/', methods=['Get'])
def mydebt():
    if not check_logged_in():
        return redirect(url_for('login'))
    db = DB(get_db())
    message = None
    mydebt = None
    try:
        (mydebt, total) = db.mydebt(session['username'])
        print(mydebt)
    except BadRequest as e:
        app.logger.error(f"{e}")
        message = "Something went wrong. Please try again"
    return render_template(
        "mydebt.html",
        total=total, 
        rows=mydebt,
        table="debt",
        message=message,
        username=session['username']
    )


########################################
## Income endpoints                   ##
########################################

@app.route('/addincome', methods=['POST'])
def addincome():
    if not check_logged_in():
        return redirect(url_for('login'))
    db = DB(get_db())
    message = "Income added successfully"
    try:
        db.addincome(session['username'], request)
    except BadRequest as e:
        app.logger.error(f"{e}")
        message = "Add income failed. Make user form input is correct"
    return redirect(url_for('myincome'))

@app.route('/myincome/', methods=['Get'])
@app.route('/myincome/<target_date>', methods=['Get'])
def myincome(target_date = None):
    if not check_logged_in():
        return redirect(url_for('login'))
    db = DB(get_db())
    message = None
    myincome = None
    print("income", target_date)
    if not target_date:
        target_date = datetime.date.today()
    else:
        target_date = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
    try:
        (myincome, total) = db.myincome(session['username'], target_date)
        print(myincome)
    except BadRequest as e:
        app.logger.error(f"{e}")
        message = "Something went wrong. Please try again"
    return render_template(
        "myincome.html",
        rows=myincome,
        total=total, 
        month=calendar.month_name[target_date.month],
        year=target_date.year,
        table="income",
        message=message,
        username=session['username']
    ) 


########################################
## Delete endpoints                   ##
########################################

@app.route('/deleterow', methods=['POST'])
def deleterow():
    if not check_logged_in():
        return redirect(url_for('login'))
    db = DB(get_db())
    message = "row deleted successfully"
    try:
        data = json.loads(request.data.decode())
        print("deleterow", data)
        db.delete_record(session['username'], data['tablename'], data['rid'])
    except BadRequest as e:
        app.logger.error(f"{e}")
        message = "Something went wrong. Please try again"
    return redirect(url_for("my{}".format(data['tablename']), message=message))


########################################
## Import endpoints                   ##
########################################
@app.route('/importcsv', methods=['GET', 'POST'])
def importcsv():
    if not check_logged_in():
        return redirect(url_for('login'))
    db = DB(get_db())
    message = None
    try:
        db.import_csvdata(session['username'], request.files['csvfile'], request.form['tablename'])
    except BadRequest as e:
        app.logger.error(f"{e}")
        message = "Something went wrong. Please try again"
    return redirect(url_for("my{}".format(request.form['tablename']), message=message))


########################################
## Utility functions                  ##
########################################

def check_logged_in():
    print(session)
    if 'username' in session:
        print("you are logged in! " + session['username'])
        return True
    print("go log in")
    return False

# connect to db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# close connectiong to db
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Create Database
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('./static/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
    

if __name__ == "__main__":
    app.run(threaded=True, port=5000, debug=False)