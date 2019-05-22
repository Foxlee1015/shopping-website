import os
import secrets
import datetime
from PIL import Image
from flask import Flask, render_template, url_for, flash, request, redirect, session, flash
from shopping_website import app, mail
from shopping_website.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, BoardForm, LocationForm, ProductForm, Submit_Form, Delete_Form
from shopping_website.shop_methods import send_reset_email, check_info, check_info2, insert_data, insert_data1, insert_data2, insert_data3, check_product, update_data, update_location, delete_data
from wtforms import Form, PasswordField, validators, StringField, SubmitField, BooleanField
from shopping_website.dbconnect import connection
from MySQLdb import escape_string as thwart
from flask_login import login_user, current_user, logout_user, login_required, LoginManager
import hashlib
import gc
from functools import wraps
from werkzeug.utils import secure_filename
from flask_mail import Message
from bs4 import BeautifulSoup
import urllib.request



def Get_product_location(product_n):
    with urllib.request.urlopen("http://service.epost.go.kr/trace.RetrieveRegiPrclDeliv.postal?sid1="+product_n) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        meaning = soup.find('div', {'id':'print'})
        Get_product_location("6664503016753") # 운송장 번호 입력 (예로 6664503016753 )

@app.context_processor
def context_processor():
    product_list, likes_count_all = check_product("product_info")
    n = len(product_list)
    categories = ['0', '여성패션', '남성패션', '뷰티', '식품', '주방용품', '생활용품' ,'홈인테리어', '가전디지털', '자동차', '완구취미', '문구', '도서']
    return dict(categories=categories, p_list=product_list, n=n, likes_count_all=likes_count_all)

@app.route("/")
@app.route("/home", methods=["GET", "POST"])
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
        rank = 0
        return render_template ('home.html', rank=rank)

@app.route('/login/', methods=["GET", "POST"])
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
            return redirect(url_for('home'))
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
                        return render_template("home.html", username=username, rank=rank)
                    else:
                        flash('Wrong password')
                        return render_template("login.html", form=form)
            gc.collect()
            return render_template("login.html", form=form)

@app.route('/register/', methods=["GET", "POST"])
def register_page():
    """
    chekc_info = email, username 중복 확인
    session['email'] = form.email.data  = form 의 이메일정보로 세션 저장
    """
    try:
        if session['logged_in'] == True:
            return redirect(url_for('home'))
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
                return redirect(url_for('home'))
        else:
            flash("Type the info")
        return render_template("register.html", form=form)

@app.route("/reset/", methods=["GET", "POST"])
def reset():
    """
    check_info = email 존재 확인
    send_reset_email = 암호리셋 링크 전송
    """
    try:
        if session['logged_in'] == True:
            return redirect(url_for('home'))
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
                return redirect(url_for('home'))
        else:
            return render_template("reset.html")

@app.route("/reset_pass/", methods=["GET", "POST"])
def reset_pass():
    """
    check_info - 이메일 존재 확인
    update-_data - 비밀번호 수정
    """
    try:
        if session['logged_in'] == True:       # 로그인 상태에서는 홈으로
            return redirect(url_for('home'))
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
                return redirect(url_for('login'))
        else:
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
        email = session['email']
        info_list = check_info("user_list", "email", email)
        username, password_db = info_list[0][1], info_list[0][2]
        if request.method == "POST" and form.validate():
            title, content, pass_data = form.title.data, form.content.data, form.password.data
            password_input = hashlib.sha256(pass_data.encode()).hexdigest()  # 입력된 비밀번호 암호화
            if password_db == password_input:
                insert_data2("board", title, content, email)
                flash(username + "님 빠른 시일 내에 연락드리겠습니다.")
                gc.collect()
                return render_template("home.html")
            else:
                flash('Wrong password')
                return render_template("board_write.html", form=form, title="board_write")
        else:
            return render_template("board_write.html", form=form, username=username, title="board_write")
    except:
        return redirect(url_for('login'))

@app.route('/board', methods=["GET","POST"])
def board_main():
    board_list = check_product("board")
    board_count_number = len(board_list)
    return render_template("board_main.html", board_list=board_list, board_count_n=board_count_number, title="board")

@app.route('/mypage', methods=["GET", "POST"])
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
        return redirect(url_for('login'))


@app.route('/register_product', methods=["GET", "POST"])
def register_product():
    """
    파일이름 random_hex
    파일저장 후 insert_data1 상품 정보 저장
    """
    random_hex = secrets.token_hex(8)
    form = ProductForm(request.form)
    email = session['email']
    rank = check_info2("rank", "user_list", "email", email)
    if rank[0][0] == None:
        flash('판매자등록을 먼저 해주십시오')
        return redirect(url_for('home'))
    if request.method == "POST" :
        product_name, product_intro, product_tag = form.product_name.data, form.product_intro.data, form.product_tag.data
        file = request.files['file']                  # post 된 파일 정보 가져옴
        if not file or file.filename=="":                                  # 파일이 존재하지 않으면
            flash('Check your file')
            return render_template("register_product.html", form=form, title="register_product")
        else:
            filename = secure_filename(file.filename)
            filename =  random_hex + filename
            #사이즈 조절
            #output_size = (200,250)
            #file = Image.open(file)
            #file.thumbnail(output_size)
            info_list =check_info("user_list", "email", email)
            username = info_list[0][1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            insert_data1("product_info", product_name, product_intro, filename, username, product_tag)
            flash('상품이 등록되었습니다.')
            return redirect(url_for('home'))
    else:
        return render_template("register_product.html", form=form)



@app.route("/wish_list",  methods=["GET", "POST"] )
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
        return redirect(url_for('home'))
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

@app.route("/product_details/<int:product_n>", methods=["GET", "POST"])              # 질문? layout 에서 자세히를 누를때 상품 번호가 주소에 포함되고 그 상품번호가 <int:product_n> 에 들어가짐
@login_required
def product_details(product_n):
    form =Submit_Form(request.form)   # LikesForm
    email = session['email']
    product_list, likes_count_all = check_product("product_info")
    n= len(product_list)
    if request.method == "POST":
        info_list =check_info("user_list", "email", email)
        uid = str(info_list[0][0])
        product_n = str(product_n)
        product_likes_list = check_info2("likes", "product_info", "product_n", product_n)
        product_uid_list = product_likes_list[0][0]
        if 1:  # 좋아요 db에 추가
            if product_uid_list == None:                                                       # 좋아요 없을 때 추가
                update_data("product_info", "likes", uid, "product_n", product_n)
                product_list, likes_count_all = check_product("product_info")                                                # 추가한 정보로 새로 가져오기
                n = len(product_list)
            elif uid in str(product_uid_list):                                                       # 이미 있는 경우
                pass
            else:                                                                             # 기존 데이터에 추가하기
                new_product_likes = str(product_uid_list) + "," + uid
                update_data("product_info", "likes", new_product_likes, "product_n", product_n)
                product_list = check_product("product_info")
                n = len(product_list)
        likes_list = check_info2("likes", "user_list", "email", email)
        # likes_list[0][0] = 기존에 장바구니에 저장된 상품 번호
        if likes_list[0][0] == None:                      # 아예 db에 likes 가 없는 경우
            update_data("user_list", "likes", product_n, "email", email)
            product_list, likes_count_all = check_product("product_info")                                     # 추가 되는 경우 update 한 후에 check_product 함수 실행
            n = len(product_list)
            flash('장바구니에 추가되었습니다.')
            return  redirect(url_for('home')) #render_template('home.html', n=n, p_list=product_list, likes_count_all=likes_count_all)
        elif product_n in likes_list[0][0]:              # 해당 상품 번호가 이미 likes에 있는 경우
            flash('이미 장바구니에 있습니다.')
            return redirect(url_for('home')) # render_template('home.html', n=n, p_list=product_list, likes_count_all=likes_count_all)
        else:
            new_list = likes_list[0][0] + "," + product_n
            update_data("user_list", "likes", new_list, "email", email)
            product_list, likes_count_all = check_product("product_info")                               # 추가 되는 경우 update 한 후에 check_product 함수 실행
            n = len(product_list)
            flash('장바구니에 추가되었습니다.')
            return redirect(url_for('home')) #render_template('home.html', n=n, p_list=product_list, likes_count_all=likes_count_all)
    else: #GET
        product_list, likes_count_all = check_product("product_info")
        n = len(product_list)
        for i in range(n):                                        # 해당 상품의 정보 가져오고(DB)
            if str(product_n) == str(product_list[i][0]):         # 해당 상품의 정보(DB)와 자세히 버튼을 누른 상품의 번호와 일치하면
                product_detail = product_list[i]
                print(product_detail)
        return render_template('product_list.html', product_detail=product_detail, title="product_datails")

def Get_location_data(product_location_number):       #(운송장번호 입력) - 현재는 예제 622781895012
        with urllib.request.urlopen("https://dictionary.cambridge.org/dictionary/english/" + verb) as response:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            meaning = soup.find('b', {'class': 'def'})
            if meaning == None:
                return None
            else:
                meaning = meaning.get_text()
                return meaning

@app.route("/location_track",  methods=["GET", "POST"] )
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
        Get_location_data()
        return render_template('location_track.html', n=n, wish_list_products=list, title="배송정보")
    else:
        return render_template('location_track.html', n=n, wish_list_products=list, title="배송정보")

@app.route("/board_update/<int:board_num>", methods=["GET", "POST"])
def board_update(board_num):
    """
    board_num 에 일치하는 정보(board_num와 db상의 행번호가 다름) 가져온 후 해당 board의 작성자와 접속자가 같은지 판단(다를 시 권한 없음)

    """
    del_form = Delete_Form(request.form)
    update_form = BoardForm(request.form)
    board_list = check_product("board")
    board_count_number = len(board_list)
    board_num=board_num
    email = session['email']
    for i in range(len(board_list)):
        if board_list[i][0] == board_num:
            number_index = i                       # 리스트에는 비어있는 부분있어 인덱스 확인 필요
    if board_list[number_index][3] != email:       #로그인 이메일과 해당 게시판의 정보 불일치
        flash('권한 없음')
        return redirect(url_for('board_main'))
    if request.method == "GET":
        return render_template("board_update.html", board_list=board_list, board_count_n=board_count_number,i=number_index,title="board_update", update_form=update_form, del_form=del_form)
    else:
        if request.method == "POST":
            board_num = str(board_num)   # 테이블 입력시 int 안됌
            if update_form.validate():
                title, content, pass_data = update_form.title.data, update_form.content.data, update_form.password.data   # 사용자 - 보드 일치 확인 필요 (이메일로 들어가므로 불필요?)
                data = [title, content, board_num]
                c, conn = connection()
                c.execute("set names utf8")  # db에 한글 저장
                c.execute("UPDATE board SET title="+data[0]+", content="+data[1]+" WHERE board_n=%s", [thwart(data[2])])    # 하나라도 리스트로 해야함
                conn.commit()
                c.close()
                conn.close()
                flash("수정되었습니다.")
                return redirect(url_for('board_main'))
            if del_form.validate():
                delete_data("board", "board_n", board_num)
                flash(board_num + '번 글 삭제되었습니다.')
                return redirect(url_for('board_main'))
            else:
                return render_template("board_update.html", board_list=board_list, board_count_n=board_count_number, i=number_index, title="board_update", update_form=update_form, del_form=del_form)

@app.route("/tag/<int:tag_num>", methods=["GET", "POST"])
def product_tag(tag_num):
    tag_num=str(tag_num)
    tag_product = check_info("product_info", "tag", tag_num)
    if tag_product == None:
        return redirect(url_for('home'))
    product_list = tag_product
    n = len(product_list)
    likes_count_all = []  # 상품 정보에서 list에 포함된 사용자 uid 의 갯수를 ,  갯수로 파악해서 다른 리스트로 html 전달
    for i in range(n):
        x = tag_product[i][4]
        if x != None:
            likes_count = x.count(',') + 1
            likes_count_all.append(likes_count)
        else:
            likes_count_all.append(0)
    try:
        form = SubmitForm(request.form) # Register_seller_Form(request.form)
        email = session['email']
        if request.method == "POST" and form.validate():
            rank = 1
            update_data("user_list", "rank", rank, "email", email)
            flash('판매자로 등록되셨습니다.')
            rank = check_info2("rank", "user_list", "email", email)  # 등록된 후 rank 가져오기
            return render_template('home.html', p_list=product_list, n=n, likes_count_all=likes_count_all, rank=rank, tag_num=tag_num)
        else:
            email = session['email']
            rank = check_info2("rank", "user_list", "email", email)
            return render_template('home.html', p_list=product_list, n=n, likes_count_all=likes_count_all, rank=rank, tag_num=tag_num)
    except:
        rank = 0
        return render_template('home.html', p_list=product_list, n=n, likes_count_all=likes_count_all, rank=rank, tag_num=tag_num)