from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def welcome():
    return render_template("index.html")

@views.route('/home')
def home():
    return render_template("home.html")

@views.route('/products')
def products():
    return render_template("products.html")
