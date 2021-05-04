from flask import Blueprint,render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/login',methods=['GET','POST'])
def login():
    data = request.form
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return render_template("logout.html")

@auth.route('/sign-up',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        contact = request.form.get('contact')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        usertype = request.form.get('usertype')
        
        if len(email) < 4:
            flash('Email must be greater than 4 characters',category='error')
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

    return render_template("signup.html") 