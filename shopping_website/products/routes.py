import os, hashlib, gc, urllib.request, secrets
from flask_babel import gettext
from PIL import Image
from flask import Flask, render_template, url_for, flash, request, redirect, session, flash, send_from_directory, Blueprint
from shopping_website.forms import ProductForm, Submit_Form, Delete_Form
from shopping_website.db.db_fuctions import update_info, check_info, check_info2, insert_data, insert_data1, insert_data2, insert_data3, check_product, update_data, update_location, delete_data
from wtforms import Form, PasswordField, validators, StringField, SubmitField, BooleanField
from shopping_website.db.dbconnect import connection
from MySQLdb import escape_string as thwart
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
from shopping_website.main.routes import login_required

product = Blueprint('product', __name__)

@product.context_processor
def context_processor():
    product_list, likes_count_all = check_product("product_info")
    n = len(product_list)
    categories = ['0', '여성패션', '남성패션', '뷰티', '식품', '주방용품', '생활용품' ,'홈인테리어', '가전디지털', '자동차', '완구취미', '문구', '도서']
    return dict(categories=categories, p_list=product_list, n=n, likes_count_all=likes_count_all)


@product.route('/register_product', methods=["GET", "POST"])
@login_required
def register_product():
    """
    파일이름 random_hex
    파일저장 후 insert_data1 상품 정보 저장
    """
    form = ProductForm(request.form)
    email = session['email']
    rank = check_info2("rank", "user_list", "email", email)
    if rank[0][0] == None:
        flash('판매자등록을 먼저 해주십시오')
        return redirect(url_for('main.home'))
    if request.method == "POST" :
        product_name, product_intro, product_tag = form.product_name.data, form.product_intro.data, form.product_tag.data
        file = request.files['file']
        if not file or file.filename=="":
            flash('Check your file')
            return render_template("register_product.html", form=form, title="register_product")
        else:
            random_hex = secrets.token_hex(8)
            filename = secure_filename(file.filename)
            filename =  random_hex + filename
            #사이즈 조절
            #output_size = (200,250)
            #file = Image.open(file)
            #file.thumbnail(output_size)
            info_list =check_info("user_list", "email", email)
            username = info_list[0][1]
            from run import app
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            insert_data1("product_info", product_name, product_intro, filename, username, product_tag)
            flash('상품이 등록되었습니다.')
            return redirect(url_for('main.home'))
    else:
        return render_template("register_product.html", form=form)

@product.route("/product_details/<int:product_n>", methods=["GET", "POST"])
@login_required
def product_details(product_n):
    form =Submit_Form(request.form)
    email = session['email']
    product_list, likes_count_all = check_product("product_info")
    n= len(product_list)
    info_list = check_info("user_list", "email", email)
    username_email = info_list[0][1]
    product_n = str(product_n)
    product_info = check_info("product_info", "product_n", product_n)
    username_product = product_info[0][5]
    if username_email == username_product:
        datamatch = True
    if username_email != username_product:
        datamatch = False
    if request.method == "POST":
        info_list =check_info("user_list", "email", email)
        uid = str(info_list[0][0])
        product_likes_list = check_info2("likes", "product_info", "product_n", product_n)
        product_uid_list = product_likes_list[0][0]
        if 1:
            if product_uid_list == None:
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
        if likes_list[0][0] == None:                      # db likes 0
            update_data("user_list", "likes", product_n, "email", email)
            product_list, likes_count_all = check_product("product_info")                                     # 추가 되는 경우 update 한 후에 check_product 함수 실행
            n = len(product_list)
            flash('장바구니에 추가되었습니다.')
            return  redirect(url_for('main.home'))
        elif product_n in likes_list[0][0]:              # 해당 상품 번호가 이미 likes에 있는 경우
            flash('이미 장바구니에 있습니다.')
            return redirect(url_for('main.home'))
        else:
            new_list = likes_list[0][0] + "," + product_n
            update_data("user_list", "likes", new_list, "email", email)
            product_list, likes_count_all = check_product("product_info")                               # 추가 되는 경우 update 한 후에 check_product 함수 실행
            n = len(product_list)
            flash('장바구니에 추가되었습니다.')
            return redirect(url_for('main.home'))
    else: #GET
        product_list, likes_count_all = check_product("product_info")
        n = len(product_list)
        for i in range(n):                                        # 해당 상품의 정보 가져오고(DB)
            if str(product_n) == str(product_list[i][0]):         # 해당 상품의 정보(DB)와 자세히 버튼을 누른 상품의 번호와 일치하면
                product_detail = product_list[i]
                print(product_detail)
        return render_template('product_list.html', product_detail=product_detail, title="product_datails", datamatch=datamatch)

@product.route("/tag/<int:tag_num>", methods=["GET", "POST"])
def product_tag(tag_num):
    tag_num=str(tag_num)
    tag_product = check_info("product_info", "tag", tag_num)
    if tag_product == None:
        return redirect(url_for('main.home'))
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

@product.route("/product_update/<int:product_n>", methods=["GET", "POST"])
def product_update(product_n):
    """
    """
    random_hex = secrets.token_hex(8)
    del_form = Delete_Form(request.form)
    update_form = ProductForm(request.form)
    product_n, product_str_n = product_n, str(product_n)
    product_list = check_info("product_info", "product_n", product_str_n)
    email = session['email']
    if request.method == "POST":
        if update_form.validate():
            product_name, product_intro, product_tag = update_form.product_name.data, update_form.product_intro.data, update_form.product_tag.data
            file = request.files['file']  # post 된 파일 정보 가져옴
            if not file or file.filename == "":  # 파일이 존재하지 않으면
                flash('Check your file')
                return redirect(url_for('main.home'))
            else:
                filename = secure_filename(file.filename)
                filename = random_hex + filename
                # 사이즈 조절
                # output_size = (200,250)
                # file = Image.open(file)
                # file.thumbnail(output_size)
                from run import app
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                update_info("product_info", product_name, product_intro, filename, product_str_n)
                flash('상품 정보가 수정되었습니다.')
                return redirect(url_for('main.home'))
        if del_form.validate():
            delete_data("product_info", "product_n", product_str_n)
            flash('글이 삭제되었습니다.')
            likes_list = check_info2("likes", "user_list", "email", email) # 기존 유저의 likes 리스트에서 제거된 상품번호 제거
            update_list = likes_list[0][0].split(',')
            update_list.remove(product_str_n)
            n = len(update_list)
            wish_list_products = ""
            for i in range(n):
                wish_list_products += update_list[i] +','
            wish_list_products = wish_list_products[0:-1] #마지막 , 제거
            update_data("user_list", "likes", wish_list_products, "email", email)  # 수정된 likes 리스트 업데이트
            return redirect(url_for('main.home'))
        else:
            flash('에러발생')
            return redirect(url_for('main.home'))
    else:
        #print('d')
        return render_template("update_product.html", product_list=product_list, title="update", update_form=update_form, del_form=del_form)

