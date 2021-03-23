import sqlite3
import csv
import hashlib
import os
from flask.cli import with_appcontext
import datetime

# helper function that converts query result to json, after cursor has executed query
def to_json(cursor):
    results = cursor.fetchall()
    headers = [d[0] for d in cursor.description]
    return [dict(zip(headers, row)) for row in results]


# Error class for when a key is not found
class KeyNotFound(Exception):
    def __init__(self, message=None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = "Key/Id not found"

    def to_dict(self):
        rv = dict()
        rv["message"] = self.message
        return rv

# Error class for when a new user has the same username
class UsernameAlreadyExists(Exception):
    def __init__(self, message=None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = "Key/Id not found"

    def to_dict(self):
        rv = dict()
        rv["message"] = self.message
        return rv


# Error class for when request data is bad
class BadRequest(Exception):
    def __init__(self, message=None, error_code=400):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = "Bad Request"
        self.error_code = error_code

    def to_dict(self):
        rv = dict()
        rv["message"] = self.message
        return rv

# hash the password and return the salt and key
def hash_password(password, salt = None):
    if not salt:
        salt = os.urandom(32) # A new salt for this user
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    print(f"hash_password: {key}")
    return (salt, key)

"""
Wraps a single connection to the database with higher-level functionality.
Holds the DB connection
"""
class DB:
    def __init__(self, connection):
        self.conn = connection

    # Simple example of how to execute a query against the DB.
    # Again never do this, you should only execute parameterized query
    # See https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.execute
    # This is the qmark style:
    # cur.execute("insert into people values (?, ?)", (who, age))
    # And this is the named style:
    # cur.execute("select * from people where name_last=:who and age=:age", {"who": who, "age": age})
    def run_query(self, query):
        c = self.conn.cursor()
        c.execute(query)
        res = to_json(c)
        self.conn.commit()
        return res

    # Run script that drops and creates all tables
    def create_db(self, create_file):
        print("Running SQL script file %s" % create_file)
        with open(create_file, "r") as f:
            self.conn.executescript(f.read())
        return '{"message":"created"}'

    def import_csvdata(self, username, file, tablename):
        c = self.conn.cursor()
        user_id = c.execute("select user_id from users where username = (?)", (username,)).fetchone()[0]

        try:
            # csv.DictReader uses first line in file for column headings by default
            rows = csv.DictReader(file.read().decode().splitlines()) # comma is default delimiter
            to_db = None
            print("table", tablename)
            if tablename == "spending":
                to_db = [(row['name'].strip().capitalize(),row['amount'].strip(),row['date'].strip(),row['category'].strip().lower(),row['owner'].strip().capitalize(),row['expense_name'].strip().capitalize(), user_id) for row in rows]
            elif tablename == "expenses":
                to_db = [(row['name'].strip().capitalize(),row['amount'].strip(),row['date'].strip(),row['category'].strip().lower(),row['owner'].strip().capitalize(), user_id) for row in rows]
            elif tablename == "goals":
                to_db = [(row['name'].strip().capitalize(),row['target'].strip(),row['amount'].strip(),row['target_date'].strip(),row['owner'].strip().capitalize(), user_id) for row in rows]
            elif tablename == "debt":
                to_db = [(row['name'].strip().capitalize(),row['amount'].strip(),row['target_date'].strip(),row['owner'].strip().capitalize(), user_id) for row in rows]
            elif tablename == "income":
                to_db = [(row['name'].strip().capitalize(),row['amount'].strip(),row['date'].strip(),row['type'].strip(),row['owner'].strip().capitalize(), user_id) for row in rows]
            else:
                raise Exception("need a valid tablename")
        except Exception as e:
            print("csv import failed: {}".format(e))
            return BadRequest(e)

        print(to_db)
        whichtable = {
            "spending":"insert into spending (name,amount,date,category,owner,expense_name,user_id) values (?,?,?,?,?,?,?)",
            "expenses":"insert into expenses (name,amount,date,category,owner,user_id) values (?,?,?,?,?,?)",
            "goals":"insert into goals (name,target,amount,target_date,owner,user_id) values (?,?,?,?,?,?)",
            "debt":"insert into debt (name,amount,target_date,owner,user_id) values (?,?,?,?,?)",
            "income":"insert into income (name,amount,date,type,owner,user_id) values (?,?,?,?,?,?)"
        }
        try:
            c.executemany(whichtable[tablename], to_db)
        except Exception as e:
            print("csv import failed: {}".format(e))
            raise BadRequest("make sure the data is formated correctly")
        c.close()
        self.conn.commit()
        return '{"message":"data imported successfully"}'


    ########################################
    ## User management                    ##
    ########################################

    def add_user(self, request):
        username = request.form['username']
        password = request.form['password']
        # encrypt password
        # https://nitratine.net/blog/post/how-to-hash-passwords-in-python/#why-you-need-to-hash-passwords
        (salt, key) = hash_password(password)
        print("salt ", salt, len(salt), "key ", key, len(key))
        c = self.conn.cursor()

        # enforce unique usernames
        c.execute("select * from users where username = (?)", (username,))
        record = c.fetchone()
        if record:
            print("The username {} already exists".format(username))
            raise UsernameAlreadyExists("username already exists")
        try:
            c.execute("insert into users (username,password) values (?,?)", (username, salt+key))
        except UsernameAlreadyExists as e:
            print("Failed to add new user: {}".format(e))
            raise BadRequest(e)
        
        c.close()
        self.conn.commit()
        return '{"message":"new user inserted"}'

    def validate_user(self, request):
        username = request.form['username']
        password = request.form['password']
        # validate password
        # https://nitratine.net/blog/post/how-to-hash-passwords-in-python/#why-you-need-to-hash-passwords
        c = self.conn.cursor()

        try:
            c.execute("select * from users where username = (?)", (username,))
            record = c.fetchone()
            if not record:
                print("No user with username {} exists".format(username))
                return False
        except Exception as e:
            print("sql error: {}".format(e))
            return False

        c.close()
        print(f"found user with that username: {record}")
        hashed_password = record[2]
        salt = hashed_password[:32] 
        key = hashed_password[32:]
        print(f"{key}")
        if (hash_password(password, salt)[1] != key):
            print("wrong password for user {}".format(username))
            return False
        
        return True


    ########################################
    ## Spending management                ##
    ########################################

    def addspending(self, username, request):
        # validate that all required info is here
        name = request.form['name'].capitalize()
        amount = request.form['amount']
        expensename = request.form['linkedExpense'].capitalize()
        category = request.form['category'].lower()
        owner = request.form['owner']
        if not owner:
            owner = username
        date = request.form['date']
        if not date:
            date = datetime.date.today().strftime("%Y-%m-%d")
        
        c = self.conn.cursor()
        # get active user
        user_id = c.execute("select user_id from users where username = (?)", (username,)).fetchone()[0]
        # get linked expense id
        expense_name = c.execute("select name from expenses where name = (?)", (expensename,)).fetchone()[0]

        try:
            c.execute("insert into spending (name,amount,date,category,owner,expense_name,user_id) values (?,?,?,?,?,?,?)", (name,amount,date,category,owner,expense_name,user_id))
        except Exception as e:
            print("Failed to add spending: {}".format(e))
            raise BadRequest(e)
            
        c.close()
        self.conn.commit()
        return '{"message":"new spending inserted"}'

    def myspending(self, username):
        # get active user
        c = self.conn.cursor()
        user_id = c.execute("select user_id from users where username = (?)", (username,)).fetchone()[0]

        try:
            c.execute(
                '''
                select strftime("%m/%d/%Y", date),name,amount,expense_name,category,owner from spending 
                where user_id = (?)
                order by date desc, name;
                ''', (user_id,) 
            )
        except Exception as e:
            print("Failed to get spending: {}".format(e))
            raise BadRequest(e)
            
        result = c.fetchall()
        c.close()
        self.conn.commit()
        return result


    ########################################
    ## Expense management                 ##
    ########################################

    def addexpense(self, username, request):
        # validate that all required info is here
        name = request.form['name'].capitalize()
        amount = request.form['amount']
        category = request.form['category'].lower()
        owner = request.form['owner']
        if not owner:
            owner = username
        date = request.form['date']
        if not date:
            date = datetime.date.today().strftime("%Y-%m-%d")
        
        # get active user
        c = self.conn.cursor()
        user_id = c.execute("select user_id from users where username = (?)", (username,)).fetchone()[0]

        # enforce unique usernames
        c.execute("select * from expenses where name = (?)", (name,))
        record = c.fetchone()
        if record:
            print("The expense name {} already exists".format(name))
            raise UsernameAlreadyExists("Expense name already exists")
        try:
            c.execute("insert into expenses (name,amount,date,category,owner,user_id) values (?,?,?,?,?,?)", (name,amount,date,category,owner,user_id))
        except Exception as e:
            print("Failed to add expense: {}".format(e))
            raise BadRequest(e)
            
        c.close()
        self.conn.commit()
        return '{"message":"new spending inserted"}'

    def myexpenses(self, username):
        # get active user
        c = self.conn.cursor()
        user_id = c.execute("select user_id from users where username = (?)", (username,)).fetchone()[0]

        try:
            c.execute(
                '''
                select strftime("%m", date),name,amount as expected,category,owner from expenses 
                where user_id = (?)
                order by date desc, name;
                ''', (user_id,)
            )
        except Exception as e:
            print("Failed to get expenses: {}".format(e))
            raise BadRequest(e)
            
        result = c.fetchall()
        c.close()
        self.conn.commit()
        return result


    ########################################
    ## Goal management                    ##
    ########################################

    def addgoal(self, username, request):
        # validate that all required info is here
        name = request.form['name']
        target = request.form['target']
        amount = request.form['amount']
        owner = request.form['owner']
        if not owner:
            owner = username
        date = request.form['date']
        
        # get active user
        c = self.conn.cursor()
        user_id = c.execute("select user_id from users where username = (?)", (username,)).fetchone()[0]

        try:
            c.execute("insert into goals (name,target,amount,target_date,owner,user_id) values (?,?,?,?,?,?)", (name,target,amount,date,owner,user_id))
        except Exception as e:
            print("Failed to add goal: {}".format(e))
            raise BadRequest(e)
            
        c.close()
        self.conn.commit()
        return '{"message":"new goal inserted"}'

    def mygoals(self, username):
        # get active user
        c = self.conn.cursor()
        user_id = c.execute("select user_id from users where username = (?)", (username,)).fetchone()[0]

        try:
            c.execute(
                '''
                select strftime("%m/%d/%Y", target_date),name,target,amount,owner from goals 
                where user_id = (?) 
                order by target_date desc, name;
                ''', (user_id,)
            )
        except Exception as e:
            print("Failed to get goals: {}".format(e))
            raise BadRequest(e)
            
        result = c.fetchall()
        c.close()
        self.conn.commit()
        return result


    ########################################
    ## Debt management                    ##
    ########################################

    def adddebt(self, username, request):
        # validate that all required info is here
        name = request.form['name'].capitalize()
        amount = request.form['amount']
        owner = request.form['owner']
        if not owner:
            owner = username
        date = request.form['date']
        
        # get active user
        c = self.conn.cursor()
        user_id = c.execute("select user_id from users where username = (?)", (username,)).fetchone()[0]

        try:
            c.execute("insert into debt (name,amount,target_date,owner,user_id) values (?,?,?,?,?)", (name,amount,date,owner,user_id))
        except Exception as e:
            print("Failed to add debt: {}".format(e))
            raise BadRequest(e)
            
        c.close()
        self.conn.commit()
        return '{"message":"new debt inserted"}'
    
    def mydebt(self, username):
        # get active user
        c = self.conn.cursor()
        user_id = c.execute("select user_id from users where username = (?)", (username,)).fetchone()[0]

        try:
            c.execute(
                '''
                select strftime("%m/%d/%Y", target_date),name,amount,owner from debt 
                where user_id = (?)
                order by target_date desc, name;
                ''', (user_id,)
            )
        except Exception as e:
            print("Failed to get debt: {}".format(e))
            raise BadRequest(e)
            
        result = c.fetchall()
        c.close()
        self.conn.commit()
        return result

    ########################################
    ## Income management                  ##
    ########################################

    def addincome(self, username, request):
        # validate that all required info is here
        name = request.form['name'].capitalize()
        amount = request.form['amount']
        owner = request.form['owner']
        type = request.form['type'].lower()
        if not owner:
            owner = username
        date = request.form['date']
        if not date:
            date = datetime.date.today().strftime("%Y-%m-%d")
        
        # get active user
        c = self.conn.cursor()
        user_id = c.execute("select user_id from users where username = (?)", (username,)).fetchone()[0]

        try:
            c.execute("insert into income (name,amount,date,type,owner,user_id) values (?,?,?,?,?,?)", (name,amount,date,type,owner,user_id))
        except Exception as e:
            print("Failed to add income: {}".format(e))
            raise BadRequest(e)
            
        c.close()
        self.conn.commit()
        return '{"message":"new income inserted"}'
    
    def myincome(self, username):
        # get active user
        c = self.conn.cursor()
        user_id = c.execute("select user_id from users where username = (?)", (username,)).fetchone()[0]

        try:
            c.execute(
                '''
                select strftime("%m/%d/%Y", date),name,amount,type,owner from income 
                where user_id = (?)
                order by date desc, name;
                ''', (user_id,)
            )
        except Exception as e:
            print("Failed to get income: {}".format(e))
            raise BadRequest(e)
            
        result = c.fetchall()
        c.close()
        self.conn.commit()
        return result
