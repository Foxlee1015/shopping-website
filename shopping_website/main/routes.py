import os
import secrets
from pytz import timezone
from datetime import datetime, date, time
from flask_babel import Babel, format_date, gettext
from PIL import Image
from flask import Flask, render_template, url_for, flash, request, redirect, session, flash, send_from_directory, Blueprint
from shopping_website import mail, babel
from shopping_website.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, BoardForm, LocationForm, ProductForm, Submit_Form, Delete_Form
from shopping_website.db.db_fuctions import order_info, update_info, check_info, check_info2, insert_data, insert_data1, insert_data2, insert_data3, insert_data4, insert_data5, check_product, update_data, update_location, delete_data, update_info1
from shopping_website.main.main_fuctions import send_reset_email, Get_ip_loca, Get_product_location, users_list
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

#app.config['JSON_AS_ASCII'] = False

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
        print(a)
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
    product_list, likes_count_all = check_product("product_info")
    n = len(product_list)
    categories_ko = ['0', '여성패션', '남성패션', '뷰티', '식품', '주방용품', '생활용품' ,'홈인테리어', '가전디지털', '자동차', '완구취미', '문구', '도서']
    categories_en = ['0', 'Female', 'Male', 'Beauty', 'Food', 'Kichen', 'Home Tools' ,'Home Design', 'Device', 'Car', 'Hobby', 'Stationary', 'Book']
    try:
        if session['language'] == 'ko':
            return dict(categories=categories_ko, p_list=product_list, n=n, likes_count_all=likes_count_all)
        elif session['language'] == 'en':
            return dict(categories=categories_en, p_list=product_list, n=n, likes_count_all=likes_count_all)
    except:
        a,b,c = Get_ip_loca()
        if a == "South Korea" or "Seoul":
            return dict(categories=categories_ko, p_list=product_list, n=n, likes_count_all=likes_count_all)
        else:
            return dict(categories=categories_en, p_list=product_list, n=n, likes_count_all=likes_count_all)

@main.route("/")
@main.route("/home", methods=["GET", "POST"])
def home():
    """
    Post = rank( '1' = 판매자)  - update_data - rank 값 0 or None -> '1'
    """
    print(users_list())
    try:
        form = Submit_Form(request.form)
        email = session['email']
        if request.method == "POST" and form.validate():
            rank = '1'
            update_data("user_list", "rank", rank, "email", email)
            flash( gettext('판매자로 등록되셨습니다.'))
            rank = check_info2("rank", "user_list", "email", email)
            points = check_info2("points", "user_list", "email", email)
            return render_template('home.html', rank=rank, points=points)
        else:
            email = session['email']
            rank = check_info2("rank", "user_list", "email", email)
            points = check_info2("points", "user_list", "email", email)
            return render_template('home.html', rank=rank, points=points)
    except:
        country, state, ip = Get_ip_loca()
        rank = 0
        #if country == "South korea":
        #    session['language'] = 'ko'
        #else:
        #    session['language'] = 'en' 
        return render_template ('home.html', rank=rank, country=country, ip=ip)

"""
# loginmanager 사용
class User:
    def __init__(self, email, username):
        self.email = email
        self.user_id = username

    def is_active(self):
        return True

    def get_id(self):
        return self.user_id
"""

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
                if check_info("user_list", "email", email) == None:
                    flash('This email doesnt exist')
                    return render_template("login.html", form=form)
                else:
                    info_list = check_info("user_list", "email", email)
                    username, password_db = info_list[0][1], info_list[0][2]
                    password_input = hashlib.sha256(pass_data.encode()).hexdigest()
                    if password_db == password_input:
                        #login_user(email)
                        session['logged_in'] = True
                        session['email'] = request.form['email']
                        flash(username + gettext('engjoy shopping'))
                        rank = check_info2("rank", "user_list", "email", email)
                        return render_template("home.html", username=username, rank=rank)
                    else:
                        flash( gettext('Wrong password'))
                        return render_template("login.html", form=form)
            gc.collect()
            return render_template("login.html", form=form)


@main.route('/register/', methods=["GET", "POST"])
def register_page():
    """
    chekc_info = email, username 중복 확인
    session['email'] = form.email.data  = form 의 이메일정보로 세션 저장
    """
    try:
        if session['logged_in'] == True:
            return redirect(url_for('main.home'))
    except:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username, email, pass_data = form.username.data, form.email.data, form.password.data
            password = hashlib.sha256(pass_data.encode()).hexdigest()
            if check_info("user_list", "email", email) != None:
                flash( gettext('That email is already taken, please choose another') )
                return render_template('register.html', form=form)
            if check_info("user_list", "username", username) != None:
                flash( gettext('That username is already taken, please choose another') )
                return render_template('register.html', form=form)
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
    try:
        if session['logged_in'] == True:
            return redirect(url_for('main.home'))
    except:
        form = RequestResetForm(request.form)
        if request.method == "POST":
            email = form.email.data
            if check_info("user_list", "email", email) == None:
                flash( gettext('This email doesnt exist') )
                return render_template("reset.html", form=form)
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
            email, password, confirm = form.email.data, form.password.data, form.confirm.data
            if password != confirm:
                flash( gettext('Check your password'))
                return render_template("reset_pass.html", form=form)
            if check_info("user_list", "email", email) == None:
                flash( gettext('This email doesnt exist'))
                return render_template("reset_pass.html", form=form)
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
    #logout_user()
    #session['logged_in'] = Fasle #.clear()  # 언어세션  설정도 clear 
    except:
        session.clear()
    #if lan:
        #session['language'] = lan
    flash( gettext('You have been logged out!'))
    gc.collect()
    #return render_template('login.html')
    return redirect(url_for('main.home'))

@main.route('/mypage', methods=["GET", "POST"])
def my_page():
    """
    Post = location_data-check_into = 기존 데이터 존재시 업데이트 => update_location / 없으면 첫 배송지 등록 insert_data3
    Get =  location_data 에서 데이터 있으면 기존 데이터 보여주고 없으면 ((""),(""),(""),(""),) -빈칸으로 출력
    """
    try:
        form = LocationForm(request.form)
        email = session['email']
        location_data = check_info("user_location", "email", email)
        if request.method == "POST" and form.validate():
            address, zipcode, phonenumber = form.address.data, form.zipcode.data, form.phonenumber.data
            if location_data != None:
                update_location(address, zipcode, phonenumber, email)
                flash( gettext('배송지 업데이트에 성공했습니다.'))
                gc.collect()
                return render_template("home.html", form=form)
            else:
                insert_data3(email, address, zipcode, phonenumber)
                flash('dd' + gexttext(" 첫 배송지 등록 되었습니다."))
                gc.collect()
                return render_template("home.html", form=form)
        else:
            if location_data != None:
                location_data_all = check_info("user_location", "email", email)
                return render_template("mypage.html", form=form, location_data_all=location_data_all, title="mypage")
            else:
                location_data_all = ((""),(""),(""),(""),)
                return render_template("mypage.html", form=form, location_data_all=location_data_all, title="mypage")
    except:
        return redirect(url_for('main.login'))

@main.route("/order_list",  methods=["GET", "POST"])
@login_required
def order_list():
    form = Submit_Form(request.form)
    email = session['email']
    list = order_info(email)
    if request.method == "POST":
        track = Get_product_location("6099732777648")
        return render_template('order_list.html', n=len(list), list=list, title="order_list", track=track, m=len(track), form=form)
    else:
        return render_template('order_list.html', title="order_list", list=list, n=len(list), form=form)

@main.route("/wish_list",  methods=["GET", "POST"] )
@login_required
def wish_list():
    """
    likes_list[0][0] ->  (('2,7,10,30',),) = (상품번호, 상품번호) 저장된 데이터로 상품 번호를 , 로 분리
    상품번호 -> [2,7,10,30] 로부터 번호 정보 - check_info - 상품정보를 -> wish_list_products 에 저장
    """
    form = Submit_Form(request.form)
    email = session['email']
    likes_list = check_info2("likes", "user_list", "email", email)
    product_numbers = likes_list[0][0]
    if product_numbers == None or product_numbers == "":
        product_list, likes_count_all = check_product("product_info")
        n = len(product_list)
        flash( gettext('등록된 상품이 없습니다.'))
        return redirect(url_for('main.home'))
    likes_product_number = product_numbers.split(',')
    n = len(likes_product_number)
    wish_list_products = []
    for i in range(n):
        if likes_product_number[i] == "":
            pass
        else:
            wish_list_products.append(check_info("product_info", "product_n", likes_product_number[i]))  # 테이블 이름, 컬럼 이름, 상품 번호
    if request.method =="POST":
        flash( gettext('구매 진행'))
        points = check_info2("points", "user_list", "email", email)
        points = int(points[0][0]) - 50*n
        points = str(points)
        none_data= "" # 구매후 지우기 
        update_info1("user_list", email, none_data, points)
        fmt = "%Y-%m-%d %H:%M:%S"
        KST = datetime.now(timezone('Asia/Seoul'))
        #now = datetime.now()
        x = KST.strftime(fmt)
        #x = '%s-%s-%s'%(now.year, now.month, now.day)
        insert_data4(email,x)
        y = check_product("user_order")
        number = str(y[-1][0])
        for i in range(len(wish_list_products)):
            insert_data5(number, str(wish_list_products[i][0][0]))
        return redirect(url_for('main.order_list'))
    else:
        return render_template('wishlist.html', n=n, wish_list_products=wish_list_products, title="wish_list")


@main.route("/location_track",  methods=["GET", "POST"] )
def location_track():
    form = Submit_Form(request.form)  # Location_track_Form
    email = session['email']             # 구매 상품으로 가져오기 해야함
    likes_list = check_info2("likes", "user_list", "email", email)  # 이메일에 저장된 likes 상품 번호$
    product_numbers = likes_list[0][0]  # 2,7  (상품번호, 상품번호) 형식에서
    likes_product_number = product_numbers.split(',')
    n = len(likes_product_number)
    list = []
    for i in range(n):
        list.append(check_info("product_info", "product_n", likes_product_number[i]))
    if request.method == "POST":
        track = Get_product_location("6099732777648")
        return render_template('location_track.html', n=n, wish_list_products=list, title="location_track", track=track, m=len(track))
    else:
        return render_template('location_track.html', n=n, wish_list_products=list, title="배송정보")


