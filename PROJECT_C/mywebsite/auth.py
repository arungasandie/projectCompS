from flask import Blueprint,render_template, request, flash
from flask import Flask , redirect, url_for, session, logging, request
from flask.globals import request
from flask.signals import message_flashed
from flask_sqlalchemy import SQLAlchemy
# to use mysql
from flask_mysqldb import MySQL
# to get data from forms
from wtforms import Form, StringField, TextAreaField, PasswordField, IntegerField, RadioField, validators
# for password encryption
from werkzeug.security import generate_password_hash,check_password_hash
from passlib.hash import sha256_crypt
from functools import wraps

auth = Blueprint('auth', __name__)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sandie'
#Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'sandra'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'projectsandra'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#Initialize MySQL
mysql = MySQL(app)

@auth.route('/login',methods=['GET','POST'])
def login():
            

    return render_template("login.html")

@auth.route('/logout')
def logout():
    return render_template("logout.html")

#Register Form Class
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=2, max = 25 )])
    email = StringField('Email', [validators.Length(min=6 , max =50)])
    contact = IntegerField('Contact')
    
    password1 = PasswordField('password2')
    usertype = RadioField('usertype')
   

@auth.route('/sign-up',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        contact = request.form.get('contact')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        usertype = request.form.get('usertype')
        

        if len(email) < 6:
            flash('Email must be greater than 6 characters',category='error')
        elif len(username) < 2:
            flash('Username must be greater than 1 character', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')
        elif len(password1) < 7:
            flash('Password must be atleast 7 characters', category='error')
        elif len(contact) < 8:
            flash('Contact must be greater than 8 digits', category='error')
        else:
            flash('Account created!', category='success')
            password = sha256_crypt.encrypt(str(password1))
            #Cursor
            cur = mysql.connection.cursor()
            
            #Execute query
            password=generate_password_hash(password1, method='sha256')
            cur.execute("INSERT INTO users(username, email, contact, password, usertype) VALUES(%s, %s, %s, %s, %s)", (username,email,contact,password,usertype))

            #Commit to DB
            mysql.connection.commit()

            #Close Connection
            cur.close()

            flash("You are now registed and can log in" , 'success')

            return redirect(url_for('auth.login'))

    return render_template("signup.html") 