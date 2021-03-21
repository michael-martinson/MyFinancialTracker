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
from markupsafe import escape
import secrets
from db import DB

# Configure application
app = Flask(__name__)

# path to database
DATABASE = './database.db'

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = secrets.token_urlsafe(50)

# default path
@app.route("/")
def home(message=None):
    if not check_logged_in():
        redirect(url_for('login'))
    app.logger.debug('Logged in as %s with message %s' % escape(session['username']), message)
    return render_template("home.html", message=message, user=escape(session['username']))

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
            return redirect(url_for('home'))
        else:
            error = 'Username or Password was empty. Please try again.'
    return render_template('login.html', newuser=False, error=error)

@app.route("/newuser", methods=["GET", "POST"])
def createuser():
    error = None
    if request.method == 'POST':
        if request.form['username'] and request.form['password']:
            db = DB(get_db())
            try:
                db.add_user(request)
                session['username'] = request.form['username']
            except Exception as e:
                app.logger.error(e)
                return render_template('login.html', newuser=True, error=error)
            return redirect(url_for('home'))
        else:
            error = 'Username or Password was empty. Please try again.'
    return render_template('login.html', newuser=True, error=error)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/addexpense', methods=['Get', 'POST'])
def addexpense():
    if not check_logged_in():
        return redirect(url_for('login'))
    if request.method == 'GET': 
        return redirect(url_for('home'))
    db = DB(get_db())
    db.addexpense(session['username'], request)
    return redirect(url_for('home'))

########################################
## Utility functions                  ##
########################################

def check_logged_in():
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
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()