import os
import secrets
import datetime
from PIL import Image
from flask import Flask, render_template, url_for, flash, request, redirect, session, flash
from shopping_website import app, mail
from shopping_website.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, BoardForm, LocationForm, ProductForm, LikesForm
from shopping_website.shop_methods import send_reset_email, check_loginfo, check_username, insert_data, insert_data_board, check_product, insert_data_product, check_likesinfo, get_product_info, update_location, insert_location, show_current_location, update_likes_product, update_1st_like
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

@app.route("/")
@app.route("/home")
def home():
    product_list = check_product()
    n = len(product_list)
    return render_template('home.html', p_list=product_list, n=n)

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
                        flash(username + "님 즐거운 쇼핑 되십시오.")
                        product_list = check_product()
                        n = len(product_list)
                        return render_template("home.html", username=username, p_list=product_list, n=n)
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
            username, email, pass_data = form.username.data, form.email.data, form.password.data
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
    try:
        if session['logged_in'] == True:       # 로그인 상태에서는 홈으로
            return redirect(url_for('home'))
    except:                                      # 로그아웃상태에서 try / excpet 없이 접근 시 에러 logged_in
        form = RequestResetForm(request.form)
        if request.method == "POST":
            email = form.email.data
            if check_loginfo(email) == None:
                flash('This email doesnt exist')
                return render_template("reset.html", form=form)
            else:
                send_reset_email(email)
                flash('Please check your email')
                return render_template("home.html")
        else:                                                          # POST 가 아닌 GET 인 경우 reset 페이지로 이동 email 입력 후 submit 하면 post
            return render_template("reset.html")

@app.route("/reset_pass/", methods=["GET", "POST"])
def reset_pass():
    try:
        if session['logged_in'] == True:       # 로그인 상태에서는 홈으로
            return redirect(url_for('home'))
    except:
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
        email = session['email']                                        # 로그인 True 상태에서 email 정보 가져오고 하단 return email 정보 제공  = email 정보 못 가져오면 에러 발생 -> login 페이지로 이동(except)
        info_list = check_loginfo(email)  # 해당 이메일의 정보 가져오기
        username, password_db = info_list[0][1], info_list[0][2]
        if request.method == "POST" and form.validate():
            title, content, pass_data = form.title.data, form.content.data, form.password.data
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
            address, zipcode, phonenumber = form.address.data, form.zipcode.data, form.phonenumber.data
            c, conn = connection()
            data = c.execute("SELECT * FROM user_location WHERE email=(%s)", [thwart(email)])
            if data != 0:     # 기존 배송 데이터가 있으면 UPDATE
                update_location(address, zipcode, phonenumber, email)
                flash("배송지 업데이트에 성공했습니다.")
                gc.collect()
                return render_template("home.html", form=form)                  # 새로 입력되는 주소로 업데이트 되고 홈으로 돌아감
            else: #data == 0:           # 기존 배송 데이터가 없으면 INSERT
                insert_location(email, address, zipcode, phonenumber)
                flash(" 소중한 정보 감사합니다.")
                gc.collect()
                return render_template("home.html", form=form)       # 데이터 입력하고 홈으로 돌아감
        else:                                                        # 로그인된 상태에서 email 정보 가져오고, 이 메일을 기반으로 저장된 데이터를 가져와서 기존의 데이터를 빈칸에 넣는다.
            c, conn = connection()
            data = c.execute("SELECT * FROM user_location WHERE email=(%s)", [thwart(email)])
            if data != 0:
                location_data_all = show_current_location(email)
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
            insert_data_product(product_name, product_intro, filename)             ## db에 저장
            product_list = check_product()                                         ## db에 저장된 테이블 리스트로 가져옴([1]이름,[2]설명,[3]파일이름)
            n = len(product_list)
            return render_template('home.html', p_list=product_list, n=n)
    else:
        return render_template("register_product.html", form=form)

@app.route("/wish_list",  methods=["GET", "POST"] )
@login_required
def wish_list():
    email = session['email']                                                                # 로그인 상태 이메일 가져오기
    likes_list = check_likesinfo(email)                                                     # 이메일에 저장된 likes 상품 번호 가져오기
    product_numbers = likes_list[0][0]                                                      # 2,7  (상품번호, 상품번호) 형식에서
    likes_product_number = product_numbers.split(',')                                       # ['2', '7'] 로 변환
    n = len(likes_product_number)                                                           #
    wish_list_products = []
    for i in range(n):                                                                      # likes 갯수 만큼 loop
        wish_list_products.append(get_product_info(likes_product_number[i]))                # 리스트에 튜플(get_product_info(상품번호))저장
    return render_template('wishlist.html', n=n, wish_list_products=wish_list_products)

@app.route("/product_details/<int:product_n>", methods=["GET", "POST"])              # 질문? layout 에서 자세히를 누를때 상품 번호가 주소에 포함되고 그 상품번호가 <int:product_n> 에 들어가짐
@login_required
def product_details(product_n):
    form =LikesForm(request.form)
    email = session['email']
    product_list = check_product()
    n= len(product_list)
    numbers = product_n - 2                               # 현재 상품 번호와 db에 순서 불일치
    if request.method == "POST":
        info_list = check_loginfo(email)
        uid = str(info_list[0][0])
        product_n = str(product_n)
        c, conn = connection()
        c.execute("set names utf8")  # db에 한글 저장
        c.execute("UPDATE product_info SET likes=%s WHERE product_n=%s", [thwart(uid), thwart(product_n)])
        conn.commit()
        c.close()
        conn.close()
        """
        # 수정 및 추가할 부분! 
        처음 저장함
        이미 있는 번호면 PASS
        추가하기 
        전에 저장한거에 대한 수정(삭제)
        갯수 어떻게 출력할 건지 생각 
        """
        likes_list = check_likesinfo(email)
        if likes_list[0][0] == None:                      # 아예 db에 likes 가 없는 경우
            update_likes_product(product_n, email)
            return render_template('home.html', n=n, p_list=product_list)
        elif product_n in likes_list[0][0]:              # 해당 상품 번호가 이미 likes에 있는 경우
            return render_template('product_list.html', n=numbers, p_list=product_list)
        else:                                                     # 이미 있고 추가로 되는 경우우
            old_list = likes_list[0][0]
            new_list = likes_list[0][0] + "," + product_n
            update_1st_like(new_list, email)
            return render_template('home.html', n=n, p_list=product_list)
    else:
        return render_template('product_list.html', n=numbers, p_list=product_list)

# 좋아요 기능