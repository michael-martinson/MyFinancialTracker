import sqlite3
import csv
import hashlib
import os
from flask.cli import with_appcontext
from datetime import date, timedelta, datetime
import calendar

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
    # cur.execute("insert into people values (%s, %s)", (who, age))
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
        c.execute("select user_id from users where username = %s", (username,))
        user_id = c.fetchone()[0]

        try:
            # csv.DictReader uses first line in file for column headings by default
            rows = csv.DictReader(file.read().decode().splitlines()) # comma is default delimiter
            to_db = None
            print("table", tablename)
            if tablename == "spending":
                to_db = [(row['name'].strip().capitalize(),row['amount'].strip(),row['date'].strip(),row['category'].strip().lower(),row['owner'].strip().capitalize(),row['expense_name'].strip().capitalize(), user_id) for row in rows]
            elif tablename == "expenses":
                to_db = [(row['name'].strip().capitalize(),row['expected'].strip(),row['due_date'].strip(),row['repeat_type'].strip().lower(),row['owner'].strip().capitalize(), user_id) for row in rows]
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
            "spending":"insert into spending (name,amount,date,category,owner,expense_name,user_id) values (%s,%s,%s,%s,%s,%s,%s)",
            "expenses":"insert into expenses (name,expected,due_date,repeat_type,owner,user_id) values (%s,%s,%s,%s,%s,%s)",
            "goals":"insert into goals (name,target,amount,target_date,owner,user_id) values (%s,%s,%s,%s,%s,%s)",
            "debt":"insert into debt (name,amount,target_date,owner,user_id) values (%s,%s,%s,%s,%s)",
            "income":"insert into income (name,amount,date,type,owner,user_id) values (%s,%s,%s,%s,%s,%s)"
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
        c = self.conn.cursor()

        # enforce unique usernames
        c.execute(f"select * from users where username = %s", (username,))
        record = c.fetchone()
        if record:
            print("The username {} already exists".format(username))
            raise UsernameAlreadyExists("username already exists")
        try:
            print((salt+key), (salt+key).hex())
            c.execute("insert into users (username,password) values (%s,%s)", (username, (salt+key).hex()))
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
            c.execute("select * from users where username = %s", (username,))
            record = c.fetchone()
            if not record:
                print("No user with username {} exists".format(username))
                return False
        except Exception as e:
            print("sql error: {}".format(e))
            return False

        c.close()
        print(f"found user with that username: {record}")
        print(record[2])
        hashed_password = bytes.fromhex(record[2])
        print(hashed_password)
        salt = hashed_password[:32] 
        key = hashed_password[32:]
        if (hash_password(password, salt)[1] != key):
            print("wrong password for user {}".format(username))
            return False
        
        return True


    ########################################
    ## All Tables                         ##
    ########################################
    def delete_record(self, username, tablename, rid):
        c = self.conn.cursor()
        # get active user
        c.execute("select user_id from users where username = %s", (username,))
        user_id = c.fetchone()[0]
        
        # users can only delete records they created
        whichtable = {
            "spending":"delete from spending where spending_id = %s and user_id = %s",
            "expenses":"delete from expenses where expense_id = %s and user_id = %s",
            "goals":"delete from goals where goal_id = %s and user_id = %s",
            "debt":"delete from debt where debt_id = %s and user_id = %s",
            "income":"delete from income where income_id = %s and user_id = %s",
        }
        try:
            c.execute(whichtable[tablename], (rid,user_id))
        except Exception as e:
            print("Failed to delete record: {}".format(e))
            raise BadRequest(e)

        c.close()
        self.conn.commit()
        return '{"message":"record deleted"}'
        

    ########################################
    ## Expense management                 ##
    ########################################

    def insert_expense(self, record):
        '''
            insert an expense given a tuple of values.
            assumes that validation has been done
            record format: (name, expected, due_date, repeat_type, owner, user_id)
        '''
        # get active user
        c = self.conn.cursor()

        # enforce unique names per month
        duedate = datetime.strptime(record[2], "%Y-%m-%d").date()
        target_month = date(duedate.year, duedate.month, 1).strftime("%Y-%m-%d")
        if duedate.month == 12:
            next_month = date(duedate.year+1, 1, 1).strftime("%Y-%m-%d")
        else: 
            next_month = date(duedate.year, duedate.month+1, 1).strftime("%Y-%m-%d")
        c.execute("select name from expenses where user_id = %s and name = %s and due_date > %s and due_date < %s", (record[5], record[0], target_month, next_month))
        res = c.fetchone()
        if res:
            print("The expense name {} already exists".format(res[0]))
            raise UsernameAlreadyExists("Expense name already exists")
        try:
            print("insert record", record)
            c.execute("insert into expenses (name,expected,due_date,repeat_type,owner,user_id) values (%s,%s,%s,%s,%s,%s)", record)
            c.execute("select expense_id from expenses where user_id = %s and name = %s", (record[5], record[0]))
        except Exception as e:
            print("Failed to add expense: {}".format(e))
            raise BadRequest(e)
            
        eid = c.fetchone()
        c.close()
        self.conn.commit()
        return eid

    def addexpense(self, username, request):
        # validate that all required info is here
        name = request.form['name'].capitalize()
        expected = request.form['expected']
        repeat_type = request.form['repeat']
        owner = request.form['owner'].capitalize()
        if not owner:
            owner = username
        edate = request.form['date']
        if not edate:
            edate = date.today().strftime("%Y-%m-%d")
        
        # get active user
        c = self.conn.cursor()
        c.execute("select user_id from users where username = %s", (username,))
        user_id = c.fetchone()[0]

        try:
            self.insert_expense((name,expected,edate,repeat_type,owner,user_id))
        except Exception as e:
            print("addexpense error: {}".format(e))
            raise BadRequest(e)
            
        c.close()
        self.conn.commit()
        return '{"message":"new expense inserted"}'

    def myexpenses(self, username, target_date):
        # get active user
        c = self.conn.cursor()
        target_month = date(target_date.year, target_date.month, 1).strftime("%Y-%m-%d")
        if target_date.month == 12:
            next_month = date(target_date.year+1, 1, 1).strftime("%Y-%m-%d")
        else: 
            next_month = date(target_date.year, target_date.month+1, 1).strftime("%Y-%m-%d")

        try: 
            c.execute("select user_id from users where username = %s", (username,))
            user_id = c.fetchone()[0]
        except Exception as e:
            raise Exception("no user_id")
        try:
            # totals per month
            c.execute("select sum(expected) from expenses where user_id = %s and due_date >= %s and due_date < %s", (user_id, target_month, next_month))
            etotal = c.fetchone()[0]
            if not etotal:
                etotal = 0
            c.execute("select sum(amount) from spending where user_id = %s and expense_name != '' and date >= %s and date < %s", (user_id, target_month, next_month))
            stotal = c.fetchone()[0]
            if not stotal:
                stotal = 0

            c.execute(
                '''
                select expense_id,to_char(due_date, 'MM/DD/YYYY'),name,expected,repeat_type,owner from expenses 
                where user_id = %s and due_date >= %s and due_date < %s or repeat_type = 'monthly'
                order by due_date asc, name;
                ''', (user_id,target_month, next_month,)
            )
            expenses = c.fetchall()
            result = []
            for e in expenses:
                c.execute("select sum(amount) from spending where user_id = %s and expense_name = %s and date >= %s and date < %s", (user_id,e[2],target_month, next_month))
                tot = c.fetchone()[0]
                if not tot:
                    tot = 0
                c.execute(
                    '''
                    select spending_id,to_char(date, 'MM/DD/YY'),name,amount,expense_name,category,owner from spending 
                    where user_id = %s and expense_name = %s and date >= %s and date < %s
                    order by date desc, name;
                    ''', (user_id, e[2], target_month, next_month)
                )
                if e[4] == "monthly":
                    dt = datetime.strptime(e[1], "%m/%d/%Y")
                    if dt.month == 12:
                        ad = date(dt.year + 1, 1, dt.day).strftime("%m/%d/%Y")
                    else:
                        ad = date(dt.year, target_date.month, dt.day).strftime("%m/%d/%Y")
                    e = (e[0], ad, e[2], e[3],e[4],e[5])
                result += [(e, tot, c.fetchall())]
        except Exception as e:
            print("Failed to get expenses: {}".format(e))
            raise BadRequest(e)

        c.close()
        self.conn.commit()
        return (result, etotal, stotal)


    ########################################
    ## Spending management                ##
    ########################################

    def addspending(self, username, request):
        # validate that all required info is here
        name = request.form['name'].capitalize()
        amount = request.form['amount']
        expensename = request.form['linkedExpense'].capitalize()
        if expensename == "":
            expensename = None
        category = request.form['category'].lower()
        owner = request.form['owner']
        if not owner:
            owner = username
        sdate = request.form['date']
        if not sdate:
            sdate = date.today().strftime("%Y-%m-%d")
        
        c = self.conn.cursor()
        # get active user
        c.execute("select user_id from users where username = %s", (username,))
        user_id = c.fetchone()[0]

        try:
            c.execute("insert into spending (name,amount,date,category,owner,expense_name,user_id) values (%s,%s,%s,%s,%s,%s,%s)", (name,amount,sdate,category,owner,expensename,user_id))
        except Exception as e:
            print("Failed to add spending: {}".format(e))
            raise BadRequest(e)
            
        c.close()
        self.conn.commit()
        return '{"message":"new spending inserted"}'

    def myspending(self, username, target_date):
        # get active user
        c = self.conn.cursor()
        target_month = date(target_date.year, target_date.month, 1).strftime("%Y-%m-%d")
        if target_date.month == 12:
            next_month = date(target_date.year+1, 1, 1).strftime("%Y-%m-%d")
        else: 
            next_month = date(target_date.year, target_date.month+1, 1).strftime("%Y-%m-%d")

        total = None
        try: 
            c.execute("select user_id from users where username = %s", (username,))
            user_id = c.fetchone()[0]
        except Exception as e:
            raise Exception("no user_id")
        try:
            c.execute("select sum(amount) from spending where user_id = %s and date >= %s and date < %s", (user_id,target_month,next_month))
            total = c.fetchone()[0]
            c.execute(
                '''
                select spending_id,to_char(date, 'MM/DD/YY'),name,amount,expense_name,category,owner from spending 
                where user_id = %s and date >= %s and date < %s
                order by date desc, name;
                ''', (user_id,target_month,next_month) 
            )
        except Exception as e:
            print("Failed to get spending: {}".format(e))
            raise BadRequest(e)
            
        result = c.fetchall()
        c.close()
        self.conn.commit()
        return (result, total)


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
        gdate = request.form['date']
        
        # get active user
        c = self.conn.cursor()
        c.execute("select user_id from users where username = %s", (username,))
        user_id = c.fetchone()[0]

        try:
            c.execute("insert into goals (name,target,amount,target_date,owner,user_id) values (%s,%s,%s,%s,%s,%s)", (name,target,amount,gdate,owner,user_id))
        except Exception as e:
            print("Failed to add goal: {}".format(e))
            raise BadRequest(e)
            
        c.close()
        self.conn.commit()
        return '{"message":"new goal inserted"}'

    def mygoals(self, username):
        # get active user
        c = self.conn.cursor()

        try: 
            c.execute("select user_id from users where username = %s", (username,))
            user_id = c.fetchone()[0]
        except Exception as e:
            raise Exception("no user_id")
        try:
            c.execute("select sum(target) from goals where user_id = %s", (user_id,))
            total = c.fetchone()[0]
            c.execute(
                '''
                select goal_id,to_char(target_date, 'MM/DD/YY'),name,target,amount,owner from goals 
                where user_id = %s 
                order by target_date desc, name;
                ''', (user_id,)
            )
        except Exception as e:
            print("Failed to get goals: {}".format(e))
            raise BadRequest(e)
            
        result = c.fetchall()
        c.close()
        self.conn.commit()
        return (result, total)


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
        ddate = request.form['date']
        
        # get active user
        c = self.conn.cursor()

        try:
            user_id = c.execute("select user_id from users where username = %s", (username,)).fetchone()[0]
            c.execute("insert into debt (name,amount,target_date,owner,user_id) values (%s,%s,%s,%s,%s)", (name,amount,ddate,owner,user_id))
        except Exception as e:
            print("Failed to add debt: {}".format(e))
            raise BadRequest(e)
            
        c.close()
        self.conn.commit()
        return '{"message":"new debt inserted"}'
    
    def mydebt(self, username):
        # get active user
        c = self.conn.cursor()

        try: 
            c.execute("select user_id from users where username = %s", (username,))
            user_id = c.fetchone()[0]
        except Exception as e:
            raise Exception("no user_id")
        try:
            total = c.fetchone()[0]
            c.execute(
                '''
                select debt_id,to_char(target_date, 'MM/DD/YY'),name,amount,owner from debt 
                where user_id = %s 
                order by target_date desc, name;
                ''', (user_id,)
            )
        except Exception as e:
            print("Failed to get debt: {}".format(e))
            raise BadRequest(e)
            
        result = c.fetchall()
        c.close()
        self.conn.commit()
        return (result, total)

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
        idate = request.form['date']
        if not idate:
            idate = date.today().strftime("%Y-%m-%d")
        
        # get active user
        c = self.conn.cursor()
        c.execute("select user_id from users where username = %s", (username,))
        user_id = c.fetchone()[0]

        try:
            c.execute("insert into income (name,amount,date,type,owner,user_id) values (%s,%s,%s,%s,%s,%s)", (name,amount,idate,type,owner,user_id))
        except Exception as e:
            print("Failed to add income: {}".format(e))
            raise BadRequest(e)
            
        c.close()
        self.conn.commit()
        return '{"message":"new income inserted"}'
    
    def myincome(self, username, target_date):
        # get active user
        c = self.conn.cursor()
        target_month = date(target_date.year, target_date.month, 1).strftime("%Y-%m-%d")
        if target_date.month == 12:
            next_month = date(target_date.year+1, 1, 1).strftime("%Y-%m-%d")
        else: 
            next_month = date(target_date.year, target_date.month+1, 1).strftime("%Y-%m-%d")

        try: 
            c.execute("select user_id from users where username = %s", (username,))
            user_id = c.fetchone()[0]
        except Exception as e:
            raise Exception("no user_id")
        try:
            c.execute("select sum(amount) from income where user_id = %s and date >= %s and date < %s", (user_id,target_month,next_month))
            total = c.fetchone()[0]
            c.execute(
                '''
                select income_id,to_char(date, 'MM/DD/YY'),name,amount,type,owner from income 
                where user_id = %s and date >= %s and date < %s
                order by date desc, name;
                ''', (user_id,target_month,next_month)
            )
        except Exception as e:
            print("Failed to get income: {}".format(e))
            raise BadRequest(e)
            
        result = c.fetchall()
        c.close()
        self.conn.commit()
        return (result, total)
