import os
import secrets
import datetime
from PIL import Image
from flask import Flask, render_template, url_for, flash, request, redirect, session, flash
from shopping_website import app, mail
from shopping_website.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, BoardForm, LocationForm, ProductForm
from wtforms import Form, PasswordField, validators, StringField, SubmitField
from shopping_website.dbconnect import connection
from MySQLdb import escape_string as thwart
from flask_login import login_user, current_user, logout_user, login_required, LoginManager
import hashlib
import gc
from functools import wraps
from werkzeug.utils import secure_filename
from flask_mail import Message

#layout list
Categories = ["여성패션", "남성패션", "뷰티", "식품", "주방용품", "생활용품"]   # html for loop? len=len(Categories), Categories=Categories)

def send_reset_email(email):
    #token = email.get_reset_token()
    msg = Message('Password reset request', sender='noreply@foxlee-shop.com', recipients=[email])
    msg.body = f''' To reset your pass, visit the following link:
http://127.0.0.1:5000/reset_pass/
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def check_loginfo(email):           #이메일 입력 -> 비밀번호 출력
    c, conn = connection()
    c.execute("set names utf8")  # db 한글 있을 시 필요
    data = c.execute("SELECT * FROM user_list WHERE email = (%s)", [thwart(email)])
    if data == 0:  # c.execute 로부터 해당 이메일이 존재하지 않으면 data == 0
        return None
    else:
        info_list = c.fetchall()
        return info_list

def check_username(username):           #이메일 입력 -> 비밀번호 출력
    c, conn = connection()
    c.execute("set names utf8")  # db 한글 있을 시 필요
    data = c.execute("SELECT * FROM user_list WHERE username = (%s)", [thwart(username)])
    if data == 0:  # c.execute 로부터 해당 username이 존재하지 않으면 data == 0
        return None
    else:
        return True  # username 이 이미 존재.

def insert_data(email, username, password):
    c, conn = connection()
    c.execute("set names utf8")  # db에 한글 저장
    c.execute("INSERT INTO user_list (username, password, email) VALUES (%s, %s, %s)", (thwart(username), thwart(password), thwart(email)))
    conn.commit()
    c.close()
    conn.close()

def insert_data_board(title, content, email):
    c, conn = connection()
    c.execute("set names utf8")  # db 한글 저장
    c.execute("INSERT INTO board (title, content, email) VALUES (%s, %s, %s)",
              (thwart(title), thwart(content), thwart(email)))
    conn.commit()
    c.close()
    conn.close()

@app.route("/")
@app.route("/home")
def home():
        return render_template('home.html')

@app.route('/login/', methods=["GET", "POST"])
def login():
    try:
        if session['logged_in'] == True:       # 로그인 상태에서는 홈으로
            return redirect(url_for('home'))
    except:          # 세션에서 오류뜰때 except = 로그인 되지 않은 상태면 log 페이지로 이동
            form = LoginForm(request.form)
            if request.method == "POST" and form.validate():
                email = form.email.data
                if check_loginfo(email) == None:
                    flash('This email doesnt exist')
                    return render_template("login.html", form=form)
                else:
                    info_list = check_loginfo(email)                             # 해당 이메일의 정보 가져오기
                    username, password_db = info_list[0][1], info_list[0][2]
                    pass_data = form.password.data
                    password_input = hashlib.sha256(pass_data.encode()).hexdigest() # 입력된 비밀번호 암호화
                    if password_db == password_input:  # 테이블에서 가져온 비번과 loginform의 비밀번호의 데이터악 일치하면   암호화 필요! sha256_crypt.verify(form.password, data):
                        session['logged_in'] = True
                        session['email'] = request.form['email']
                        flash(username + "님 즐거운 쇼핑 되십시오. You are now logged in")
                        return render_template("home.html", username=username)
                    else:
                        flash('Wrong password')
                        return render_template("login.html", form=form) # error=error
            gc.collect()
            return render_template("login.html", form=form)

@app.route('/register/', methods=["GET", "POST"])
def register_page():
    try:
        if session['logged_in'] == True:
            return redirect(url_for('home'))
    except:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            pass_data = form.password.data
            password = hashlib.sha256(pass_data.encode()).hexdigest()
            if check_loginfo(email) != None:
                flash("That email is already taken, please choose another")
                return render_template('register_test.html', form=form)
            if check_username(username) != None:
                flash("That username is already taken, please choose another")
                return render_template('register_test.html', form=form)
            else:
                insert_data(email, username, password)
                gc.collect()
                flash("Thanks for registering!")
                session['logged_in'] = True
                session['email'] = form.email.data  #request.form['email']  # 처음 가입할때 기입한 이메일로 접속하도록 설정
                return redirect(url_for('home'))
        else:
            flash("Type the info")
        return render_template("register_test.html", form=form)

@app.route("/reset/", methods=["GET", "POST"])
def reset():
    #if session['logged_in'] == True:       # 로그인 상태에서는 홈으로
    #    return redirect(url_for('home'))
    form = RequestResetForm(request.form)
    if request.method == "POST":
        email = form.email.data
        if check_loginfo(email) == None:
            flash('This email doesnt exist')
            return render_template("reset.html", form=form)
        else:
            send_reset_email(email)
            flash('Please check your email')                               # 메일보내기 필요 //
            return render_template("home.html")
    else: # POST 가 아닌 GET 인 경우 reset 페이지로 가서 email 넣고 post
        return render_template("reset.html")

@app.route("/reset_pass/", methods=["GET", "POST"])
def reset_pass():
    #if session['logged_in'] == True:       # 로그인 상태에서는 홈으로
    #    return redirect(url_for('home'))
    form = ResetPasswordForm(request.form)
    if request.method == "POST":
        email = form.email.data
        password = form.password.data
        confirm = form.confirm.data
        if password != confirm:
            flash('Check your password')
            return render_template("reset_pass.html", form=form)
        if check_loginfo(email) == None:
            flash('This email doesnt exist')
            return render_template("reset_pass.html", form=form)
        else:
            password = hashlib.sha256(password.encode()).hexdigest()
            c, conn = connection()
            change_pass = c.execute("UPDATE user_list SET password = (%s) WHERE email = (%s)", [thwart(password), thwart(email)])
            conn.commit()  # 업데이트한 후 반드시 필요!
            flash('Success')
            return redirect(url_for('login'))  # 비번 바꾼후 login 으로 이동
    else: # POST 가 아닌 GET 인 경우 reset 페이지로 가서 email 넣고 post
        return render_template("reset_pass.html")

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))
    return wrap

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('home'))

@app.route('/board_write', methods=["GET", "POST"])
def board_page():
    try:
        form = BoardForm(request.form)
        email = session['email']                                  # 로그인 True 상태에서 email 정보 가져오고 하단 return email 정보 제공
        info_list = check_loginfo(email)  # 해당 이메일의 정보 가져오기
        username, password_db = info_list[0][1], info_list[0][2]
        if request.method == "POST" and form.validate():
            title = form.title.data
            content = form.content.data
            pass_data = form.password.data
            password_input = hashlib.sha256(pass_data.encode()).hexdigest()  # 입력된 비밀번호 암호화
            if password_db == password_input:
                insert_data_board(title, content, email)
                flash(username + "님 빠른 시일 내에 연락드리겠습니다.")
                gc.collect()
                return render_template("home.html")

            else:
                flash('Wrong password')
                return render_template("board_write.html", form=form)
        else:
            return render_template("board_write.html", form=form, username=username)
    except:
        return redirect(url_for('login'))

@app.route('/board', methods=["GET","POST"])
def board_main():
    c, conn = connection()
    board_count = c.execute("SELECT board_n FROM board")                           # 게시된 글의 수.
    board_count_number = board_count                                               # board_count_number 수 저장
    board_n_list = c.fetchall()                                                   # c.exectue 에서 게시판의 넘버 정보 가져오기
    board_list = [[None for k in range(4)] for j in range(board_count_number)]    # 갯수에 맞춰 데이터가 들어갈 2차 행렬
    for x in range(board_count_number):                                            # 게시글의 수 loop
        count_number = str(board_n_list[x][0])                                     # 튜플에 저장된 게실글의 넘버만 가져와서 문자열로( thart에 들어갈 문자열 )   board_n_list = ((1,),(2,),(3,),(6,)) 처럼 저장됨
        for i in range(4):                                                         # i 0~3 (보드넘버, 제목, 내용, 이메일)
            c.execute("set names utf8")                                            # 한글 데이터
            board_data = c.execute("SELECT * FROM board WHERE board_n = (%s)", [thwart(count_number)])  # count_number = 게시글의 넘버 // 보드 넘버를 기준으로 보드넘버, 제목, 내용, 이메일 가져옴
            board_data1 = c.fetchone()[i]
            board_list[x][i] = board_data1                                         # 가져온 데이터 리스트에 저장
    return render_template("board_main.html", board_list=board_list, board_count_n=board_count_number)

@app.route('/mypage', methods=["GET", "POST"])
def my_page():
    try:
        form = LocationForm(request.form)
        email = session['email']          #로그인된 상태에서의 이메일 정보 가져와서 db에 아래 정보와 같이 저장
        if request.method == "POST" and form.validate():
            address = form.address.data
            zipcode = form.zipcode.data
            phonenumber = form.phonenumber.data
            c, conn = connection()
            data = c.execute("SELECT * FROM user_location WHERE email=(%s)", [thwart(email)])
            if data != 0:     # 기존 배송 데이터가 있으면 UPDATE
                c, conn = connection()
                c.execute("set names utf8") # 배송 정보 한글 저장.
                print(phonenumber)
                c.execute("UPDATE user_location SET address=(%s), zipcode=(%s), phonenumber=(%s)  WHERE email=(%s)", [thwart(address), thwart(zipcode), thwart(phonenumber), thwart(email)])             # phonenumber 업데이트 실패  -> 컬럼 특성이 int라서?
                conn.commit()
                flash("배송지 업데이트에 성공했습니다.")
                c.close()
                gc.collect()
                return render_template("home.html", form=form)                  # 새로 입력되는 주소로 업데이트 되고 홈으로 돌아감

            else: #data == 0:           # 기존 배송 데이터가 없으면 INSERT
                c, conn = connection()
                c.execute("set names utf8") # 배송 정보 한글 저장.
                c.execute("INSERT INTO user_location (email, address, zipcode, phonenumber) VALUES (%s, %s, %s, %s)", thwart(email), thwart(address), thwart(zipcode), thwart(phonenumber))
                conn.commit()
                flash(" 소중한 정보 감사합니다.")
                c.close()
                gc.collect()
                return render_template("home.html", form=form)       # 데이터 입력하고 홈으로 돌아감
        else:                                                        # 로그인된 상태에서 email 정보 가져오고, 이 메일을 기반으로 저장된 데이터를 가져와서 기존의 데이터를 빈칸에 넣는다.
            c, conn = connection()
            data = c.execute("SELECT * FROM user_location WHERE email=(%s)", [thwart(email)])
            if data != 0:
                c.execute("set names utf8")
                location_data = c.execute("SELECT * FROM user_location WHERE email=(%s)", [thwart(email)])
                location_data_all = c.fetchall()
                return render_template("mypage.html", form=form, location_data_all=location_data_all)
            else:
                location_data_all = ((""),(""),(""),(""),)   # data == 0 인 경우에는 db에 location data 가 없으므로 빈 행렬로 html 에 빈칸으로 출력
                return render_template("mypage.html", form=form, location_data_all=location_data_all)
    except:
        return redirect(url_for('login'))

@app.route('/register_product', methods=["GET", "POST"])                        #  << 실수, methods get, post 추가 안함 >>
def register_product():
    random_hex = secrets.token_hex(8)
    form = ProductForm(request.form)
    if request.method == "POST" :
        product_name = form.product_name.data
        product_intro = form.product_intro.data
        file = request.files['file']                  # post 된 파일 정보 가져옴
        if not file:                                  # 파일이 존재하지 않으면
            flash('no file')
            return render_template("register_product.html", form=form)
        if file.filename == "":
            flash('no name of file')
            return render_template("register_product.html", form=form)
        else:
            filename = secure_filename(file.filename)
            filename =  random_hex + filename
            #사이즈 조절
            #output_size = (200,250)
            #file = Image.open(file)
            #file.thumbnail(output_size)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            c, conn = connection()
            c.execute("set names utf8")
            c.execute("INSERT INTO product_info (product_name, product_intro, filename) VALUES (%s, %s, %s)", [thwart(product_name), thwart(product_intro), thwart(filename)])
            conn.commit()
            product_list = check_product()
            n = len(product_list)
            return render_template('product_list.html', p_list=product_list, n=n)   #### DB에 저장해서 넘버와 파일이름 저장해서 같이 저장, 같이 불러오기
    else:
        return render_template("register_product.html", form=form)

def check_product():           #이메일 입력 -> 비밀번호 출력
    c, conn = connection()
    c.execute("set names utf8")  # db 한글 있을 시 필요
    data = c.execute("SELECT * FROM product_info")
    product_list = c.fetchall()
    return product_list

@app.route("/product_list")
def product_list():
    product_list  = check_product()
    n = len(product_list)
    return render_template('product_list.html', p_list=product_list, n=n)