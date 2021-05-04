from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL


def create_app():
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

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    return app