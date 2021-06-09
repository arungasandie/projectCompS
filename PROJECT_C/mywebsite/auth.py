
from subprocess import STARTF_USESTDHANDLES
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

#------------------------user log in------------------------------------
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

#-----Check if user logged in--------------------------------------------------------------
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized Please login", 'danger')
            return redirect(url_for('auth.login'))
    return wrap
#-----logout---------------------------------------------------------------------------------------
@auth.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out' , 'success')
    return redirect(url_for('auth.loginoption'))    


#---- log in as user or admin--------------------------------------------------------------------------
@auth.route('/loginoptions')
def loginoption():
    return render_template("loginoptions.html")



#-----Register Form Class-----------------------------------------------------------------------------------
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=2, max = 25 )])
    email = StringField('Email', [validators.Length(min=6 , max =50)])
    contact = IntegerField('Contact')
    
    password1 = PasswordField('password2')
    usertype = RadioField('usertype')
   
#--------------sign up ---------------------------------------------------------------------------------------
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

            return redirect(url_for('auth.loginoption'))

    return render_template('signup.html')


#-------------user checking cart---------------------------------------------------------------------------------------------------------------------
@auth.route('/cart')
@is_logged_in
def cart():
    cur = mysql.connection.cursor()
    username = session['username']
    result = cur.execute("SELECT sales.sale_id, sales.item_id, sales.quantity, sales.delivery_place, sales.date_of_order, sales.date_of_delivery, sales.subtotal, sales.status, sales.cardnumber, stock.item_name, stock.item_price, users.username FROM sales JOIN users ON sales.username = users.username JOIN stock ON sales.item_id = stock.item_id WHERE sales.status='PLACED' AND sales.username = %s",[username])
    cart = cur.fetchall()
    if result < 1:
        msg="No items found found"
        return render_template('cart.html', msg =  msg)
    else:
        return render_template('cart.html', cart=cart)
    
    cur.close()
    return render_template("cart.html")


#-----------customer ordering----------------------------------------------------------------------------------------------------------------
class OrderForm(Form):  # Create Order Form
    itemname=StringField('Item name')
    creditcardnumber = StringField('CardNumber')
    quantity = IntegerField('Quantity')
    order_place = StringField('Place')


@auth.route('/addtocart/<string:id>' ,methods=['GET','POST'])
@is_logged_in
def addtocart(id):
    cur = mysql.connection.cursor()
    # get product id
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
        itemprice=cur.execute("SELECT item_price FROM stock WHERE item_id = %s",[id])
        if itemprice > 0:
            #Get stored hash
            itemp = cur.fetchone()
            priceofitem = itemp['item_price']
        subtotal = priceofitem * int(quantity)

        #Get user by username
        cur.execute("INSERT INTO sales (item_id, quantity, username, cardnumber, delivery_place, subtotal, status) VALUES (%s,%s,%s,%s,%s,%s, 'PLACED')",(id, quantity, username, cardno, orderplace, subtotal))
        # update subtotal
        
        # update stock table by minusing amount ordered
        cur.execute("UPDATE stock SET items_available= items_available- %s WHERE item_id = %s",(quantity, id))

        #commit to database 
        mysql.connection.commit()
         
        #Close Connection
        cur.close()

        flash("Order has been made" , 'success')

        return redirect(url_for('auth.cart'))

    return render_template('order.html',product=product)


#-----------customer editing order--------------------------------------------   
@auth.route('/editorder/<string:id>', methods = ['GET','POST'])
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

#-------------------customer deleting order
@auth.route('/deleteorder/<string:id>')
@is_logged_in
def delete_order(id):
    cur = mysql.connection.cursor()
    # get item id to update stock
    itemid=cur.execute("SELECT item_id FROM sales WHERE sale_id = %s ",[id])
    if itemid > 0:
            item_id = cur.fetchone()
            item_id1 = item_id['item_id']
    # get quantity to update stock
    quantityb=cur.execute("SELECT quantity FROM sales WHERE sale_id = %s ",[id])
    if quantityb > 0:
            quantitybo = cur.fetchone()
            quantitybought = quantitybo['quantity']

    #delete sale
    cur.execute("DELETE FROM sales WHERE sale_id = %s AND status = 'PLACED' ", [id])

    # update stock table 
    cur.execute("UPDATE stock SET items_available= items_available + %s WHERE item_id = %s",(quantitybought , item_id1))
    mysql.connection.commit()

    cur.close()

    flash("Order deleted", 'success')

    return redirect(url_for('auth.cart'))
#------------customer done shopping--------------------------------------------------------------------------------------------------
@auth.route('/checkout')
def checkout():
    return render_template("checkout.html")


#-----------MANAGER VIEW -------------------------------------------------------------------------------------------------------------

#--------------------admin log in---------------------------------

@auth.route('/adminlogin',methods=['GET','POST'])
def admin_login():
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
            usertype=data['usertype']

            #Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                if usertype=='admin':
                    app.logger.info('PASSWORD MATCH')
                    #Passed
                    session['admin_logged_in'] = True
                    session['username'] = username

                    flash("You are now logged in" , 'success')
                    return redirect(url_for('auth.mhome'))
                else:
                    flash("Login only for admin!", category='error')
                    return render_template('loginoptions.html')
            else:
                flash('Invalid login', category='error')
                app.logger.info('PASSWORD NOT MATCHED')
                return render_template('adminlogin.html')
            
            #close connection
            cur.close()

        else:
            flash('Username not found',category='error')
            return render_template('adminlogin.html')

    return render_template('adminlogin.html') 

#check if admin is logged in
def admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized Please login", 'danger')
            return redirect(url_for('auth.admin_login'))
    return wrap

#-----------------------logout-------------------------------------------------------------------------------------------------------------
@auth.route('/adminlogout')
@admin_logged_in
def adminlogout():
    session.clear()
    flash('You are now logged out' , 'success')
    return redirect(url_for('auth.loginoption'))

#-----top 2 items bought by quantity----------------------------------------------------------------------------------------------------------
def top2quantity():
    cur = mysql.connection.cursor()
    top2quantity = cur.execute("SELECT * FROM (SELECT sales.item_id, SUM(sales.quantity) 'TotalQty' , stock.item_name FROM sales JOIN stock ON stock.item_id = sales.item_id GROUP BY sales.item_id ORDER BY SUM(sales.quantity) DESC , sales.item_id ASC) A LIMIT 2;")
    top2qty = cur.fetchall()
    cur.close()
    return top2qty

#-----top 2 items bought by price----------------------------------------------------------------------------------------------------------
def top2price():
    cur = mysql.connection.cursor()
    top2price = cur.execute("SELECT * FROM (SELECT sales.item_id, SUM(sales.quantity) 'TotalQty', MAX(stock.item_price) 'ItemPrice' , stock.item_name FROM sales JOIN stock ON stock.item_id = sales.item_id GROUP BY sales.item_id ORDER BY MAX(stock.item_price) DESC , sales.item_id ASC) A LIMIT 2;")
    top2prc = cur.fetchall()
    cur.close()
    return top2prc

#-----top customer on sales ----------------------------------------------------------------------------------------------------------
def topcust():
    cur = mysql.connection.cursor()
    topcust= cur.execute("SELECT * FROM ( SELECT sales.username, SUM(sales.subtotal) 'Totalsales', users.c_id  FROM sales JOIN stock ON stock.item_id = sales.item_id JOIN users ON sales.username = users.username  GROUP BY sales.username ORDER BY SUM(sales.subtotal) DESC, users.c_id ASC ) A LIMIT 1;")
    topcustomer = cur.fetchall()
    cur.close()
    return topcustomer

#-----admin home(products and top 2 products) ----------------------------------------------------------------------------------------------------------
@auth.route('/mhome')
@admin_logged_in
def mhome():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM stock")
    products = cur.fetchall()
    top2qty = top2quantity()
    top2prc = top2price()
   
    if result > 0 :
        return render_template('managerhome.html' ,products=products, top2qty=top2qty, top2prc= top2prc)
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

#---------------------------all sales made(delivered, placed and damaged)-------------------------------------------------------------
@auth.route('/msales')
@admin_logged_in
def msales():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT sales.sale_id, stock.item_id,stock.item_name, sales.username, sales.cardnumber, sales.quantity, sales.date_of_order, sales.date_of_delivery, sales.delivery_place, sales.subtotal, sales.status FROM sales JOIN stock ON sales.item_id = stock.item_id")
    sales = cur.fetchall()
    top2qty = top2quantity()
    if result > 0 :
        return render_template('msales.html' , sales=sales)
    else:
        msg = "No products found"
        return render_template('msales.html', msg =  msg)

    return render_template('msales.html')
#----------------------------products that are out of stock---------------------------------------------------------------------------------------------------------------------
@auth.route('/outofstock')
def outofstock():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM stock WHERE items_available = 0")
    outofstock = cur.fetchall()

    if result > 0 :
        return render_template('outofstock.html' , outofstock=outofstock)
    else:
        msg = "No products found"
        return render_template('outofstock.html', msg =  msg)

    return render_template('outofstock.html')

#----------------------------all customers + top customer---------------------------------------------------------------------------------------------------------------------
@auth.route('/customers')
def customers():
    cur = mysql.connection.cursor()
    topcustomer = topcust()
    result = cur.execute("SELECT * FROM users WHERE NOT usertype='admin'")
    users = cur.fetchall()
     
    if result > 0 :
        return render_template('customerslist.html' , users = users, topcustomer=topcustomer)
    else:
        msg = "No customers found"
        return render_template('customerslist.html', msg =  msg)

    return render_template('customerslist.html')

#----------------------------orders placed ---------------------------------------------------------------------------------------------------------------------
@auth.route('/customersorders')
def customersorders():
    cur = mysql.connection.cursor()
    result=cur.execute("SELECT sales.sale_id, stock.item_id, stock.item_name, sales.username, sales.cardnumber, sales.quantity, sales.date_of_order, sales.date_of_delivery, sales.delivery_place, sales.subtotal, sales.status FROM sales JOIN stock ON sales.item_id = stock.item_id WHERE status = 'PLACED'")
    orders = cur.fetchall()

    if result > 0 :
        return render_template('customerorder.html' , orders=orders)
    else:
        msg = "No orders found"
        return render_template('customerorder.html', msg =  msg)

    return render_template('customerorder.html')

#----------------------------orders delivered---------------------------------------------------------------------------------------------------------------------
@auth.route('/deliveries')
def deliveries():
    cur = mysql.connection.cursor()
    result=cur.execute("SELECT sales.sale_id, stock.item_id, stock.item_name, sales.username, sales.cardnumber, sales.quantity, sales.date_of_order, sales.date_of_delivery, sales.delivery_place, sales.subtotal, sales.status FROM sales JOIN stock ON sales.item_id = stock.item_id WHERE status = 'DELIVERED'")
    deliveries = cur.fetchall()

    if result > 0 :
        return render_template('deliveries.html' , deliveries=deliveries)
    else:
        msg = "No deliveries found"
        return render_template('deliveries.html', msg =  msg)

    return render_template('deliveries.html')

#----------------------------orders damaged ---------------------------------------------------------------------------------------------------------------------
@auth.route('/damaged')
def damaged():
    cur = mysql.connection.cursor()
    result=cur.execute("SELECT sales.sale_id, stock.item_id, stock.item_name, sales.username, sales.cardnumber, sales.quantity, sales.date_of_order, sales.date_of_delivery, sales.delivery_place, sales.subtotal, sales.status FROM sales JOIN stock ON sales.item_id = stock.item_id WHERE status = 'DAMAGED'")
    orders = cur.fetchall()

    if result > 0 :
        return render_template('damaged.html' , orders=orders)
    else:
        msg = "No orders found"
        return render_template('damaged.html', msg =  msg)

    return render_template('damaged.html')

#----------------------------products delivered to comapany---------------------------------------------------------------------------------------------------------------------
@auth.route('/cdeliveries')
def cdeliveries():
    cur = mysql.connection.cursor()
    result=cur.execute("SELECT companyorders.delivery_id, stock.item_id, stock.item_name, companyorders.username, companyorders.quantity, companyorders.date_of_order, companyorders.delivery_to_store_address, companyorders.status FROM companyorders JOIN stock ON companyorders.item_id = stock.item_id")
    cdeliveries = cur.fetchall()

    if result > 0 :
        return render_template('cdeliveries.html' , cdeliveries=cdeliveries)
    else:
        msg = "No deliveries found"
        return render_template('cdeliveries.html', msg =  msg)

    return render_template('cdeliveries.html')

#------------------- staff edits status of sale------------------------------------------------------------------------- 
@auth.route('/editsale/<string:id>', methods = ['GET','POST'])
@admin_logged_in
def edit_sale(id):
    #Create Cursor
    cur = mysql.connection.cursor()
    #Get order by ID
    result = cur.execute("SELECT * FROM sales WHERE sale_id = %s", [id])
    order = cur.fetchone()

    #Get form details 
    if request.method == 'POST':
        cur = mysql.connection.cursor() 
        
        status = request.form.get('status')
        username=session['username']
        #Create Cursor
        cur = mysql.connection.cursor()

        #Execute
        cur.execute("UPDATE sales SET status = %s WHERE sale_id = %s",(status, id))

        #Commit to DB
        mysql.connection.commit()

        #Close Connection
        cur.close()
        flash("Order Updated", 'success')

        return redirect(url_for('auth.msales'))

    return render_template('admineditorder.html', order=order)  

#-----------------Delete Sale---------------------------------------------------------
@auth.route('/deletesale/<string:id>')
@is_logged_in
def delete_sale(id):
    cur = mysql.connection.cursor()

    itemid=cur.execute("SELECT item_id FROM sales WHERE sale_id = %s ",[id])
    if itemid > 0:
            #Get stored hash
            item_id = cur.fetchone()
            item_id1 = item_id['item_id']

 

    quantityb=cur.execute("SELECT quantity FROM sales WHERE sale_id = %s ",[id])
    if quantityb > 0:
            #Get stored hash
            quantitybo = cur.fetchone()
            quantitybought = quantitybo['quantity']

    #delete sale
    cur.execute("DELETE FROM sales WHERE sale_id = %s AND status = 'PLACED' ", [id])

    # update stock table 
    cur.execute("UPDATE stock SET items_available= items_available + %s WHERE item_id = %s",(quantitybought , item_id1))
    mysql.connection.commit()

    cur.close()

    flash("Order deleted", 'success')

    return redirect(url_for('auth.msales'))

#---- ordering item as staff ----------------------------------------------------------------------------------------
@auth.route('/orderoutof/<string:id>' , methods=['GET','POST'])
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




