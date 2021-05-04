from flask import Flask, render_template,url_for,flash,redirect,url_for,session,logging,request
from flask.globals import request
from flask.signals import message_flashed
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt 

#instance of flask class
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')