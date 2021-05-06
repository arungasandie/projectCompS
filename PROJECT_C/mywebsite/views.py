from flask import Blueprint, render_template
from flask import Blueprint,render_template, request, flash
from flask import Flask , redirect, url_for, session, logging, request
from flask.globals import request
from flask.signals import message_flashed
from flask_sqlalchemy import SQLAlchemy
# to use mysql
from flask_mysqldb import MySQL

views = Blueprint('views', __name__)
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
@views.route('/')
def welcome():
    return render_template("index.html")

@views.route('/home')
def home():
    return render_template("home.html")

@views.route('/products')
def products():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM stock")
    products = cur.fetchall()

    if result > 0 :
        return render_template('products.html' ,products=products)
    else:
        msg = "No products found"
        return render_template('products.html', msg =  msg)

    #Close connection
    cur.close()
    return render_template("products.html")
