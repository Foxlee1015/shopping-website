import os
from flask import Flask
#from flask_login import LoginManager
from werkzeug.utils import secure_filename
from flask_mail import Mail
from flask_babel import Babel

UPLOAD_FOLDER = 'shopping_website/static/images/'                             # 사진 저장위치는 run.py 기준!
UPLOAD_FOLDER_usb = '/home/pi/rs_usb/Pictures_usb/images/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

mail=Mail()
babel=Babel()

def create_app():
    app = Flask(__name__)
    app.jinja_env.auto_reload= True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['UPLOAD_FOLDER_usb'] = UPLOAD_FOLDER_usb
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['MYSQL_USE_UNICODE'] = True
    #login_manager = LoginManager()
    #login_manager.init_app(app)
    #login_manager.login_view = 'main.login'
    #login_manager.login_message_category = 'info'
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = ***
    app.config['MAIL_PASSWORD'] = ***
    mail.init_app(app)
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    babel.init_app(app)

    from shopping_website.main.routes import main
    from shopping_website.board.routes import board
    from shopping_website.products.routes import product
    from shopping_website.admin.routes import admin

    app.register_blueprint(main)
    app.register_blueprint(board)
    app.register_blueprint(product)
    app.register_blueprint(admin)

    return app
