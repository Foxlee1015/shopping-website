from flask import Flask
from flask_login import LoginManager
"""
from flask_mail import Mail
from dbconnect import connection
from MySQLdb import escape_string as thwart
import hashlib
import gc
from functools import wraps
"""

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from shopping_website import routes
