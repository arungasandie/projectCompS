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
        password1 = request.form.get('password')
        username = request.form.get('password2')
        usertype = request.form.get('usertype')
        
        if len(email) < 4:
            pass
        elif len(username) < 2:
            pass
        elif password1 != password2:
            pass
        elif len(password) < 7:
            pass
        elif len(contact) < 8:
            pass
        else:
            pass
    return render_template("signup.html") 