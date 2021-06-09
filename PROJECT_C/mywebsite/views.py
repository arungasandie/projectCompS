from mywebsite.auth import is_logged_in, admin_logged_in
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

#---------------view products home page and categories -------------------------
def laptop():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM stock WHERE group_id = 1 AND items_available >= 1;")
    laptops = cur.fetchall()
    cur.close()

    return laptops

def phone():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM stock WHERE group_id = 2 AND items_available >= 1;")
    phones = cur.fetchall()
    cur.close()

    return phones

def audio():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM stock WHERE group_id = 3 AND items_available >= 1;")
    audio = cur.fetchall()
    cur.close()

    return audio

#Initialize MySQL
mysql = MySQL(app)
@views.route('/')
def welcome():
    session.clear()
    return render_template("index.html")

@views.route('/home')
def home():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM stock WHERE group_id = 1 AND items_available >= 1;")
    laptops = laptop()
    phones = phone()
    audios = audio()
    if result > 0 :
        return render_template('home.html' ,laptops=laptops, phones=phones, audios=audios)
    else:
        msg = "No laptops found"
        return render_template('home.html', homemsg =  msg)
    
    return render_template('home.html')

@views.route('/products/<string:id>/')
def product(id):
    #Create Cursor
    cur = mysql.connection.cursor()
    #Get articles
    result = cur.execute("SELECT * FROM stock WHERE item_id = %s",[id])
    product = cur.fetchone()
    if result > 0:
        return render_template('view_product.html', product=product)
        
    else:
        msg = "Product was not found"
        return render_template('view_product.html', msg =  msg)
      
    #Close connection
    cur.close()
    return render_template("view_product.html")



@views.route('/products')
def products():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM stock WHERE items_available >= 1")
    products = cur.fetchall()

    if result > 0 :
        return render_template('products.html' ,products=products)
    else:
        msg = "No products found"
        return render_template('products.html', msg =  msg)

    #Close connection
    cur.close()
    return render_template("products.html")

#--------------view laptops -----------------------------------
@views.route('/laptops')
def viewlaptops():
    products=laptop()
    return render_template("products.html", products=products)

#--------------view phones -----------------------------------
@views.route('/phones')
def viewphones():
    products=phone()
    return render_template("products.html", products=products)

#--------------view audio -----------------------------------
@views.route('/audioequipment')
def viewaudio():
    products=audio()
    return render_template("products.html", products=products)














    
