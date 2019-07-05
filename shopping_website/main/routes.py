import os
import secrets
from pytz import timezone
from datetime import datetime, date, time
from flask_babel import Babel, format_date, gettext
from PIL import Image
from flask import Flask, render_template, url_for, flash, request, redirect, session, flash, send_from_directory, Blueprint
from shopping_website import mail, babel
from shopping_website.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, BoardForm, LocationForm, ProductForm, Submit_Form, Delete_Form
from shopping_website.db.db_functions import order_info, update_info, check_info, check_info2, insert_data, insert_data1, insert_data2, insert_data3, insert_data4, insert_data5, check_product, update_data, update_location, delete_data, update_info1, likes_info, get_userid, get_userinfo
from shopping_website.main.main_functions import send_reset_email, Get_ip_loca, Get_product_location, users_list
from wtforms import Form, PasswordField, validators, StringField, SubmitField, BooleanField
from shopping_website.db.dbconnect import connection
from MySQLdb import escape_string as thwart
import hashlib
import gc
from werkzeug.utils import secure_filename
from flask_mail import Message
from bs4 import BeautifulSoup
import urllib.request
from babel import numbers, dates
import re
from functools import wraps

main = Blueprint('main', __name__)


@main.route('/uploads/<path:filename>')
def download_file(filename):
    from run import app
    return send_from_directory(app.config['UPLOAD_FOLDER_usb'],filename, as_attachment=True)


@babel.localeselector
def get_locale():
    """
    1. 세션에 저장되어 있는 언어 2.Ip 주소로 한국이면 한국어 그외 영어로 설정
    """
    try:
        language = session['language']
        return language
    except:
        a, b, c = Get_ip_loca()
        if a == "South Korea":
            session['language'] = 'ko'
            return 'ko'
        else:
            session['language'] = 'en'
            return 'en'
        #return app.config['BABEL_DEFAULT_LOCALE']
        #return request.accept_languages.best(['en', 'ko'])  # 사용자의 위치에 따라 언어 바뀜(best, 가능한 옵션중(나의 경우. 영어, 한국어)



@main.route("/language/<language>")
def language(language):
    if not language in ['ko', 'en']:
        language = 'en'
    session['language'] = language
    return redirect(url_for('main.home'))


@main.context_processor
def context_processor():

    # Total product information and likes info
    product_list = check_product("product_info")
    n = len(product_list)
    x = likes_info()
    likes_count = []
    seller_list = []
    for i in range(n):
        z = len([ item[0] for item in x if item[1] == product_list[i][0] ])
        likes_count.append(z)
        seller = get_userinfo("user_list","uid", str(product_list[i][5]))
        seller_list.append(seller[0][1])

    #Product category
    categories_ko = ['0', '여성패션', '남성패션', '뷰티', '식품', '주방용품', '생활용품' ,'홈인테리어', '가전디지털', '자동차', '완구취미', '문구', '도서']
    categories_en = ['0', 'Female', 'Male', 'Beauty', 'Food', 'Kichen', 'Home Tools' ,'Home Design', 'Device', 'Car', 'Hobby', 'Stationary', 'Book']
    try:

        # session is established
        if session['language'] == 'ko':
            return dict(categories=categories_ko, p_list=product_list, count = likes_count, n=n, seller=seller_list)
        elif session['language'] == 'en':
            return dict(categories=categories_en, p_list=product_list, count = likes_count, n=n, seller=seller_list)
    except:

        # session is expired or no session 
        a,b,c = Get_ip_loca()
        if a == "South Korea" or "Seoul":
            return dict(categories=categories_ko, p_list=product_list, count = likes_count, n=n, seller=seller_list)
        else:
            return dict(categories=categories_en, p_list=product_list, count = likes_count, n=n, seller=seller_list)

@main.route("/")
@main.route("/home", methods=["GET", "POST"])
def home():

    # A user is logged in
    try:
        form = Submit_Form(request.form)
        email = session['email']
        points = check_info2("points", "user_list", "email", email)
        if request.method == "POST" and form.validate():

            # Register as a seller ( rank = 1 )
            rank = '1'
            update_data("user_list", "rank", rank, "email", email)
            flash( gettext('판매자로 등록되셨습니다.'))
            return render_template('home.html', rank=rank, points=points)
        else:
            email = session['email']
            rank = check_info2("rank", "user_list", "email", email)
            return render_template('home.html', rank=rank, points=points)

    # A user is not logged in
    except:
        country, state, ip = Get_ip_loca()
        rank = 0
        return render_template ('home.html', rank=rank, country=country, ip=ip)

@main.route('/login/', methods=["GET", "POST"])
def login():
    """
    로그인 상태 -> 홈으로 리턴
    check_info("user_list", "email", email) - 저장된 email 중복 확인
    info_list = check_info("user_list", "email", email) - 해당 이메일의 username, password 가져옴
    비밀번호 일치 확인 후 로그인
    해당 이메일의 rank 확인
    :return:
    """
    try:
        if session['logged_in'] == True:
            return redirect(url_for('main.home'))
    except:
        form = LoginForm(request.form)
        if request.method == "POST" and form.validate():
            email, pass_data = form.email.data, form.password.data

            # Check if the email exists
            if check_info("user_list", "email", email) == None:
                flash('This email doesnt exist')
                return render_template("login.html", form=form)

            else:
                # Check password
                info_list = check_info("user_list", "email", email)
                username, password_db = info_list[0][1], info_list[0][2]
                password_input = hashlib.sha256(pass_data.encode()).hexdigest()

                # A uers is logged in
                if password_db == password_input:
                    session['logged_in'] = True
                    session['email'] = request.form['email']
                    flash(username + gettext('engjoy shopping'))
                    rank = check_info2("rank", "user_list", "email", email)
                    return render_template("home.html", username=username, rank=rank)

                # failed to log in
                else:
                    flash( gettext('Wrong password'))
                    return render_template("login.html", form=form)
        else:
            return render_template("login.html", form=form)


@main.route('/register/', methods=["GET", "POST"])
def register_page():
    """
    chekc_info = email, username 중복 확인
    session['email'] = form.email.data  = form 의 이메일정보로 세션 저장
    """


    #Go back to main page if user is logged in
    try:
        if session['logged_in'] == True:
            return redirect(url_for('main.home'))

    except:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username, email, pass_data = form.username.data, form.email.data, form.password.data
            password = hashlib.sha256(pass_data.encode()).hexdigest()

            # Failed - email exists
            if check_info("user_list", "email", email) != None:
                flash( gettext('That email is already taken, please choose another') )
                return render_template('register.html', form=form)

            # Failed - username exists
            if check_info("user_list", "username", username) != None:
                flash( gettext('That username is already taken, please choose another') )
                return render_template('register.html', form=form)

            # Save a new user information, the user is logged in
            else:
                insert_data("user_list",username, password, email)
                gc.collect()
                flash( gettext('Thanks for registering!') )
                session['logged_in'] = True
                session['email'] = form.email.data
                return redirect(url_for('main.home'))
        else:
            flash( gettext('Type the info') )
        return render_template("register.html", form=form)

@main.route("/reset/", methods=["GET", "POST"])
def reset():
    """
    check_info = email 존재 확인
    send_reset_email = 암호리셋 링크 전송
    """

    # Redirect to homepage when an user is logged_in
    try:
        if session['logged_in'] == True:
            return redirect(url_for('main.home'))

    except:
        form = RequestResetForm(request.form)
        if request.method == "POST":
            email = form.email.data

            # Check if the email exists
            if check_info("user_list", "email", email) == None:
                flash( gettext('This email doesnt exist') )
                return render_template("reset.html", form=form)

            # Send an email to the email
            else:
                send_reset_email(email)
                flash( gettext('Please check your email') )
                return redirect(url_for('main.home'))
        else:
            return render_template("reset.html")

@main.route("/reset_pass/", methods=["GET", "POST"])
def reset_pass():
    """
    check_info - 이메일 존재 확인
    update-_data - 비밀번호 수정
    """
    try:
        if session['logged_in'] == True:
            return redirect(url_for('main.home'))
    except:
        form = ResetPasswordForm(request.form)
        if request.method == "POST":

            # Check the information
            email, password, confirm = form.email.data, form.password.data, form.confirm.data

            # password and confirm are not same
            if password != confirm:
                flash( gettext('Check your password'))
                return render_template("reset_pass.html", form=form)

            # Check if the email exists
            if check_info("user_list", "email", email) == None:
                flash( gettext('This email doesnt exist'))
                return render_template("reset_pass.html", form=form)

            # Save a new password
            else:
                password = hashlib.sha256(password.encode()).hexdigest()
                update_data("user_list", "password", password, "email", email)
                flash(gettext('Success'))
                return redirect(url_for('main.login'))
        else:
            return render_template("reset_pass.html")

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('main.login'))
    return wrap

@main.route("/logout/")
@login_required
def logout():
    try:
        if session['language']:
            lan = session['language']
        session.clear()
        session['language'] = lan
    except:
        session.clear()
    flash( gettext('You have been logged out!'))
    gc.collect()
    return redirect(url_for('main.home'))

@main.route('/mypage', methods=["GET", "POST"])
def my_page():
    """
    Post = location_data-check_into = 기존 데이터 존재시 업데이트 => update_location / 없으면 첫 배송지 등록 insert_data3
    Get =  location_data 에서 데이터 있으면 기존 데이터 보여주고 없으면 ((""),(""),(""),(""),) -빈칸으로 출력
    """
    form = LocationForm(request.form)
    email = session['email']
    user_id = str(get_userid(email))
    rank = check_info2("rank", "user_list", "email", email)
    location_data = check_info("user_location", "user_id", user_id)

    if request.method == "POST" and form.validate():
        address, zipcode, phonenumber = form.address.data, form.zipcode.data, form.phonenumber.data

        # Update an address
        if location_data != None:
            update_location(address, zipcode, phonenumber, user_id)
            flash( gettext('배송지 업데이트에 성공했습니다.'))
            return render_template("home.html", form=form, rank=rank)

        # A new address
        else:
            insert_data3(user_id, address, zipcode, phonenumber)
            flash( gettext(' 첫 배송지 등록 되었습니다.'))
            return render_template("home.html", form=form, rank=rank)

    else:
        # Return my_page with an old address
        if location_data != None:
            location_data_all = check_info("user_location", "user_id", user_id)
            return render_template("mypage.html", form=form, location_data_all=location_data_all, title="mypage")

        # Return empty my_page
        else:
            location_data_all = ((""),(""),(""),(""),)
            return render_template("mypage.html", form=form, location_data_all=location_data_all, title="mypage")


@main.route("/order_list",  methods=["GET", "POST"])
@login_required
def order_list():
    form = Submit_Form(request.form)
    email = session['email']
    user_id = get_userid(email)
    list = order_info(str(user_id))
    if request.method == "POST":
        track = Get_product_location("6063453062801")
        return render_template('order_list.html', n=len(list), list=list, title="order_list", track=track, m=len(track), form=form)
    else:
        return render_template('order_list.html', title="order_list", list=list, n=len(list), form=form)


@main.route("/wish_list",  methods=["GET", "POST"] )
@login_required
def wish_list():
    """
    GET : 해당 이메일의 user_id -> 좋아요 수(len(z)) 확인 // wish_list
    POST : 주문 생성 , 기존 장바구니 지우기
    """
    form = Submit_Form(request.form)
    email = session['email']
    x = likes_info()
    y = get_userid(email)
    user_id = str(y)

    # products likes when user_id is y
    z = [list[1] for list in x if list[0] == y ]
    if z == []:
        flash( gettext('등록된 상품이 없습니다.'))
        return redirect(url_for('main.home'))
    wish_list = []
    n = len(z)
    for i in range(n):
        wish_list.append(check_info("product_info", "product_n", str(z[i])))

    if request.method =="POST":

        # Check the price
        flash( gettext('구매 진행'))
        user_info = get_userinfo("user_list","uid",user_id)
        points = user_info[0][6]
        for i in range(n):
            product_info = get_userinfo("product_info", "product_n", str(z[i]))
            price = product_info[0][7]
            points -= price

        # Update a point
        points = str(points)
        update_info1("user_list", email, points) # 포인트 업데이트

        # Empty a cart
        delete_data("user_cart", "user_id", user_id)

        # Create an order
        fmt = "%Y-%m-%d %H:%M:%S"
        KST = datetime.now(timezone('Asia/Seoul'))
        x = KST.strftime(fmt)  #x = '%s-%s-%s'%(now.year, now.month, now.day)
        insert_data4(user_id,x)
        y = check_product("user_order")
        number = str(y[-1][0])
        for i in range(len(wish_list)):
            insert_data5(number, str(wish_list[i][0][0]))
        return redirect(url_for('main.order_list'))
    else:
        return render_template('wishlist.html', n=n, wish_list_products=wish_list, title="wish_list")

