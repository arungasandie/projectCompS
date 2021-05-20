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

#---------------view products home page-------------------------
def laptop():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM stock WHERE group_id = 1 AND items_available >= 1;")
    laptops = cur.fetchall()
    cur.close

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

@views.route('/addtocart/<string:id>' ,methods=['GET','POST'])
@is_logged_in
def addtocart(id):
    cur = mysql.connection.cursor()
    #Get articles
    result = cur.execute("SELECT * FROM stock WHERE item_id = %s",[id])
    product = cur.fetchone()

    if request.method == 'POST':
        cur = mysql.connection.cursor()
        
        cardno = request.form.get('cardnumber')
        quantity = request.form.get('quantity')
        orderplace = request.form.get('delivery_place')
        username=session['username']

        # get user id
        cid=cur.execute("SELECT c_id FROM users WHERE username= %s", [username])
        c_id= cur.fetchone()
        # get price 
        item_price=cur.execute("SELECT item_price FROM stock WHERE item_id = %s",[id])
        price=cur.fetchone()

        #Get user by username
        cur.execute("INSERT INTO sales (item_id, quantity, username, cardnumber, delivery_place, status) VALUES (%s,%s,%s,%s,%s,'PLACED')",(id, quantity, username, cardno, orderplace ))
        # update stock table 
        cur.execute("UPDATE stock SET items_available= items_available- %s WHERE item_id = %s",(quantity, id))

        #commit to database 
        mysql.connection.commit()
         
        #Close Connection
        cur.close()

        flash("Order has been made" , 'success')

        return redirect(url_for('auth.cart'))

    return render_template('order.html',product=product)

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

 #-----------edit order--------------------------------------------   

@views.route('/editorder/<string:id>', methods = ['GET','POST'])
@is_logged_in
def edit_order(id):
    #Create Cursor
    cur = mysql.connection.cursor()
    #Get order by ID
    result = cur.execute("SELECT * FROM sales WHERE sale_id = %s", [id])
    order = cur.fetchone()

    #Get form details 
    if request.method == 'POST':
        cur = mysql.connection.cursor() 
        cardno = request.form.get('cardnumber')
        quantity = request.form.get('quantity')
        orderplace = request.form.get('delivery_place')
        username=session['username']
        #Create Cursor
        cur = mysql.connection.cursor()

        #Execute
        cur.execute("UPDATE sales SET cardnumber = %s, quantity = %s, delivery_place = %s WHERE sale_id = %s",(cardno , quantity, orderplace, id))

        #Commit to DB
        mysql.connection.commit()

        #Close Connection
        cur.close()
        flash("Order Updated", 'success')

        return redirect(url_for('auth.cart'))

    return render_template('edit_order.html', order=order)    

@views.route('/base')
def base():
    return render_template('base.html')

#---- ordering item as manager-----------------------------
@views.route('/orderoutof/<string:id>' , methods=['GET','POST'])
@admin_logged_in
def companyorder(id):
    cur = mysql.connection.cursor()
    #Get articles
    result = cur.execute("SELECT * FROM stock WHERE item_id = %s",[id])
    product = cur.fetchone()

    if request.method == 'POST':
        cur = mysql.connection.cursor()
        quantity = request.form.get('quantity')
        orderplace = request.form.get('delivery_to_store_address')
        username=session['username']

        #Get user by username
        cur.execute("INSERT INTO companyorders (item_id, quantity, delivery_to_store_address, username,  status) VALUES (%s,%s,%s,%s,'PLACED')",(id, quantity, orderplace, username, ))
        #commit to database 
        mysql.connection.commit()
         
        #Close Connection
        cur.close()

        flash("Order has been made" , 'success')

        return redirect(url_for('auth.cdeliveries'))

    return render_template('corder.html',product=product)

@views.route('/links')
def rr():
    return redirect(url_for('https://www.youtube.com/watch?v=dQw4w9WgXcQ'))











    
