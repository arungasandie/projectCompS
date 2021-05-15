from mywebsite.views import product
from mywebsite.views import home
from flask import Blueprint,render_template, request,flash
from flask import Flask , redirect, url_for, session, logging, request
from flask.globals import request
from flask.signals import message_flashed
from flask_sqlalchemy import SQLAlchemy
# to use mysql
from flask_mysqldb import MySQL
# to get data from forms
from wtforms import Form, StringField, TextAreaField, PasswordField, IntegerField, RadioField, form, validators
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
    if request.method == 'POST':
        #Get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        #Create Cursor
        cur = mysql.connection.cursor()

        #Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            #Get stored hash
            data = cur.fetchone()
            password = data['password']

            #Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                app.logger.info('PASSWORD MATCH')
                #Passed
                session['logged_in'] = True
                session['username'] = username

                flash("You are now logged in" , 'success')
                return redirect(url_for('views.home'))
            else:
                error = 'Invalid login'
                app.logger.info('PASSWORD NOT MATCHED')
                return render_template('login.html', error = error)
            
            #close connection
            cur.close()

        else:
            error = 'Username not found'
            return render_template('login.html', error = error)

    return render_template('login.html') 

#Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized Please login", 'danger')
            return redirect(url_for('login'))
    return wrap

@auth.route('/loginoptions')
def loginoption():
    return render_template("loginoptions.html")

@auth.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out' , 'success')
    return redirect(url_for('auth.login'))

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
        
        password = sha256_crypt.encrypt(str(password1))

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
            
            #Cursor
            cur = mysql.connection.cursor()
            
            #Execute query
            cur.execute("INSERT INTO users(username, password, email, contact, usertype) VALUES(%s, %s, %s, %s,%s)", (username,password,email,contact,usertype))

            #Commit to DB
            mysql.connection.commit()

            #Close Connection
            cur.close()

            flash("You are now registed and can log in" , 'success')

            return redirect(url_for('auth.login'))

    return render_template('signup.html')



@auth.route('/cart')
@is_logged_in
def cart():
    cur = mysql.connection.cursor()
    username = session['username']
    cur.execute("SELECT sum(subtotal) FROM sales")
    total=cur.fetchone() 
    result = cur.execute("SELECT sales.sale_id, sales.item_id, sales.quantity, stock.item_name, stock.item_price, users.username FROM sales JOIN users ON sales.c_id = users.c_id JOIN stock ON sales.item_id = stock.item_id WHERE users.username = %s",[username])
    cart = cur.fetchall()
    if result < 1:
        msg="No items found found"
        return render_template('cart.html', msg =  msg)
    else:
        return render_template('cart.html', cart=cart)
    
    cur.close()
    return render_template("cart.html")



@auth.route('/addtocart/<string:id>',methods=['GET','POST'])
def addtocart(id):
    if request.method == 'POST':
        username = session['username']
        #Get form fields
        quantity = request.form['quantity']

        #Create Cursor
        cur = mysql.connection.cursor()

        #Get user by username
        cur.execute("INSERT INTO sales (item_id, username, quantity, status) VALUES (%s,%s,%s,'PLACED')",(id, username, quantity))
        #commit to database 
        mysql.connection.commit()
         
        #Close Connection
        cur.close()

        flash("Product added to cart" , 'success')

        return redirect(url_for('views.home'))

    return render_template('products.html')

           
#Delete Product
@auth.route('/deleteproduct/<string:id>')
@is_logged_in
def delete_product(id):
    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM sales WHERE sale_id = %s ", [id])

    mysql.connection.commit()

    cur.close()

    flash("Order deleted", 'success')

    return redirect(url_for('auth.cart'))

@auth.route('/mhome')
def mhome():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM stock")
    products = cur.fetchall()

    if result > 0 :
        return render_template('managerhome.html' ,products=products)
    else:
        msg = "No products found"
        return render_template('managerhome.html', msg =  msg)

    res = cur.execute("SELECT * FROM sales")
    sales = cur.fetchall()
    if res < 1:
        msg="No sales found"
        return render_template('managerhome.html', msg =  msg)
    #Close connection
    cur.close()
    return render_template("managerhome.html")

@auth.route('/checkout')
def checkout():
    return render_template("checkout.html")
    