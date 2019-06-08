import os
import secrets
from datetime import datetime, date, time
from flask_babel import Babel, format_date, gettext
from PIL import Image
from flask import Flask, render_template, url_for, flash, request, redirect, session, flash, send_from_directory, Blueprint
from shopping_website import mail, babel
from shopping_website.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, BoardForm, LocationForm, ProductForm, Submit_Form, Delete_Form
from shopping_website.db.db_fuctions import update_info, check_info, check_info2, insert_data, insert_data1, insert_data2, insert_data3, check_product, update_data, update_location, delete_data
from shopping_website.main.main_fuctions import send_reset_email, Get_ip_loca, Get_product_location
from wtforms import Form, PasswordField, validators, StringField, SubmitField, BooleanField
from shopping_website.db.dbconnect import connection
from MySQLdb import escape_string as thwart
from flask_login import login_user, current_user, logout_user, login_required, LoginManager
import hashlib
import gc
from functools import wraps
from werkzeug.utils import secure_filename
from flask_mail import Message
from bs4 import BeautifulSoup
import urllib.request
from babel import numbers, dates
import re

main = Blueprint('main', __name__)

@main.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_usb'],filename, as_attachment=True)

@main.context_processor
def context_processor():
    product_list, likes_count_all = check_product("product_info")
    n = len(product_list)
    categories = ['0', '여성패션', '남성패션', '뷰티', '식품', '주방용품', '생활용품' ,'홈인테리어', '가전디지털', '자동차', '완구취미', '문구', '도서']
    return dict(categories=categories, p_list=product_list, n=n, likes_count_all=likes_count_all)

@main.route("/")
@main.route("/home", methods=["GET", "POST"])
def home():
    """
    Post = rank( '1' = 판매자)  - update_data - rank 값 0 or None -> '1'
    """
    try:
        form = Submit_Form(request.form)
        email = session['email']
        if request.method == "POST" and form.validate():
            rank = '1'
            update_data("user_list", "rank", rank, "email", email)
            flash('판매자로 등록되셨습니다.')
            rank = check_info2("rank", "user_list", "email", email)
            return render_template('home.html', rank=rank)
        else:
            email = session['email']
            rank = check_info2("rank", "user_list", "email", email)
            return render_template('home.html', rank=rank)
    except:
        city, state, ip = Get_ip_loca()
        rank = 0
        return render_template ('home.html', rank=rank, city=city, ip=ip)

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
                        session['logged_in'] = True
                        session['email'] = request.form['email']
                        flash(username + "님 즐거운 쇼핑 되십시오.")
                        rank = check_info2("rank", "user_list", "email", email)
                        #user = User(email, username)
                        #login_user(user)
                        #next_page = request.args.get('next')
                        #return redirect(next_page) if next_page else redirect(url_for('main.home'))
                        return render_template("home.html", username=username, rank=rank)
                    else:
                        flash('Wrong password')
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
                flash("That email is already taken, please choose another")
                return render_template('register.html', form=form)
            if check_info("user_list", "username", username) != None:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)
            else:
                insert_data("user_list",username, password, email)
                gc.collect()
                flash("Thanks for registering!")
                session['logged_in'] = True
                session['email'] = form.email.data
                return redirect(url_for('main.home'))
        else:
            flash("Type the info")
        return render_template("register.html", form=form)

@main.route("/reset/", methods=["GET", "POST"])
def reset():
    """
    check_info = email 존재 확인
    send_reset_email = 암호리셋 링크 전송
    """
    try:
        if session['logged_in'] == True:
            return redirect(url_for('.main.home'))
    except:
        form = RequestResetForm(request.form)
        if request.method == "POST":
            email = form.email.data
            if check_info("user_list", "email", email) == None:
                flash('This email doesnt exist')
                return render_template("reset.html", form=form)
            else:
                send_reset_email(email)
                flash('Please check your email')
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
        if session['logged_in'] == True:       # 로그인 상태에서는 홈으로
            return redirect(url_for('main.home'))
    except:
        form = ResetPasswordForm(request.form)
        if request.method == "POST":
            email, password, confirm = form.email.data, form.password.data, form.confirm.data
            if password != confirm:
                flash('Check your password')
                return render_template("reset_pass.html", form=form)
            if check_info("user_list", "email", email) == None:
                flash('This email doesnt exist')
                return render_template("reset_pass.html", form=form)
            else:
                password = hashlib.sha256(password.encode()).hexdigest()
                update_data("user_list", "password", password, "email", email)
                flash('Success')
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
        session['language'] in ['en', 'ko']
        lang = session['language']
        session.clear() #세션에 저장된 언어 정보도 사라짐
        session['language'] = lang
    except:
        session.clear()
    flash("You have been logged out!")
    gc.collect()
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
                flash("배송지 업데이트에 성공했습니다.")
                gc.collect()
                return render_template("home.html", form=form)
            else:
                insert_data3(email, address, zipcode, phonenumber)
                flash(" 첫 배송지 등록 되었습니다.")
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
    if product_numbers == None:
        product_list, likes_count_all = check_product("product_info")
        n = len(product_list)
        flash('등록된 상품이 없습니다.')
        return redirect(url_for('main.home'))
    likes_product_number = product_numbers.split(',')
    n = len(likes_product_number)
    wish_list_products = []
    for i in range(n):
        wish_list_products.append(check_info("product_info", "product_n", likes_product_number[i]))  # 테이블 이름, 컬럼 이름, 상품 번호
    if request.method =="POST":
        flash('구매 진행')
        return render_template('wishlist.html', n=n, wish_list_products=wish_list_products, title="wish_list")
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


