import sqlite3
import hashlib
import os
from flask.cli import with_appcontext

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

    def add_user(self, request):
        username = request.form['username']
        password = request.form['password']
        # encrypt password
        # https://nitratine.net/blog/post/how-to-hash-passwords-in-python/#why-you-need-to-hash-passwords
        (salt, key) = hash_password(password)
        print("salt ", salt, len(salt), "key ", key, len(key))
        c = self.conn.cursor()

        try:
            c.execute("insert into users (username,password) values (?,?)", (username, salt+key))
        except Exception as e:
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
                print("No user with username {} exists: {}".format(username, e))
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
