import os
from flask import Flask
from flask_login import LoginManager
from werkzeug.utils import secure_filename
from flask_mail import Mail
from flask_babel import Babel


UPLOAD_FOLDER = 'shopping_website/static/images/'                             # 사진 저장위치는 run.py 기준!
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.jinja_env.auto_reload= True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dh16931@gmail.com' # os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = 'rbhs svci fmwm atpv' #os.environ.get('EMAIL_PASS')
mail = Mail(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
babel = Babel(app)

from shopping_website import routes
