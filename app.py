import os
import logging

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

logger = logging.getLogger(__name__)
# Set the logging level (e.g., DEBUG, INFO, ERROR)
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler('logfile.log')

# Set the level for the file handler
file_handler.setLevel(logging.DEBUG)

# Create a formatter to specify the log message format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Set the formatter for the file handler
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# load environment
load_dotenv()

# initiate db, login_manager
db = SQLAlchemy()
login_manager = LoginManager()
# create the app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")
env = os.getenv("FLASK_ENV")
# configure the SQLite database, relative to the app instance folder\
if env == 'production':
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI_PROD")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI_DEV")
# initialize the app with the extension
db.init_app(app)
# initialize login manager
login_manager.init_app(app)
login_manager.login_view = "login"
# mail
email = Mail(app)

import auth
import models
import sasai
import mail
import user

# from models import User

with app.app_context():
    db.create_all()
