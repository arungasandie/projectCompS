from flask import Flask, render_template,url_for

#instance of flask class
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')