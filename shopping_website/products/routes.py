import os, hashlib, gc, urllib.request, secrets
from flask_babel import gettext
from PIL import Image
from flask import Flask, render_template, url_for, flash, request, redirect, session, flash, send_from_directory, Blueprint
from shopping_website.forms import ProductForm, Submit_Form, Delete_Form
from shopping_website.db.db_functions import get_userid, update_info, check_info, check_info2, insert_data, insert_data1, insert_data2, insert_data3, check_product, update_data, update_location, delete_data, insert_data6, likes_info, check_cart, get_userinfo
from wtforms import Form, PasswordField, validators, StringField, SubmitField, BooleanField
from shopping_website.db.dbconnect import connection
from MySQLdb import escape_string as thwart
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
from shopping_website.main.routes import login_required

product = Blueprint('product', __name__)

@product.context_processor
def context_processor():
    product_list = check_product("product_info")
    n = len(product_list)
    likes_count_all = [ 0 for i in range(100) ]
    categories = ['0', '여성패션', '남성패션', '뷰티', '식품', '주방용품', '생활용품' ,'홈인테리어', '가전디지털', '자동차', '완구취미', '문구', '도서']
    return dict(categories=categories, p_list=product_list, n=n, likes_count_all=likes_count_all)


@product.route('/register_product', methods=["GET", "POST"])
@login_required
def register_product():
    """
    파일이름 random_hex
    파일저장 후 insert_data1 상품 정보 저장
    """
    random_hex = secrets.token_hex(8)
    form = ProductForm(request.form)
    email = session['email']
    user_id = get_userid(email)
    rank = check_info2("rank", "user_list", "email", email)
    price = "50"
    if rank[0][0] == None:
        flash( gettext('rg_seller'))
        return redirect(url_for('main.home'))
    if request.method == "POST" :
        product_name, product_intro, product_tag = form.product_name.data, form.product_intro.data, form.product_tag.data
        file = request.files['file'] 
        if not file or file.filename=="":
            flash( gettext('Upload a file or Check your file'))
            return render_template("register_product.html", form=form, title="register_product")
        else:
            filename = secure_filename(file.filename)
            filename =  random_hex + filename
            info_list =check_info("user_list", "email", email)
            username = info_list[0][1]
            from run import app
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file.close()
            insert_data1("product_info", product_name, product_intro, filename, str(user_id), product_tag, price)
            flash(gettext('success'))
            return redirect(url_for('main.home'))
    else:
        return render_template("register_product.html", form=form)

@product.route("/product_details/<int:product_n>", methods=["GET", "POST"])
@login_required
def product_details(product_n):
    form =Submit_Form(request.form)
    email = session['email']
    user_id = get_userid(email)
    get_likes = likes_info()
    u_idforproduct = [list[0] for list in get_likes if list[1] == product_n ]
    count_likes = len(u_idforproduct)

    # 구매자(로그인한아이디) - 판매자(글올린아이디)
    buyer = user_id
    product_list = check_info("product_info", "product_n", str(product_n))
    seller = product_list[0][5]
    if buyer == seller :
        datamatch = True
    if buyer != seller :
        datamatch = False

    if request.method == "POST":
        p = check_cart("user_cart", "user_id", "product_id", str(user_id) ,str(product_n) )
        if p: # 장바구니에 이미 있다면
            flash( gettext('already in a cart'))
            return redirect(url_for('main.home'))
        else:
            insert_data6("user_cart", str(user_id), str(product_n))
            flash( gettext('added') )
            return  redirect(url_for('main.home'))
    else:
        product_list = check_info("product_info", "product_n", str(product_n))
        n = len(product_list)
        return render_template('product_list.html', product_detail=product_list[0], title="product_datails", datamatch=datamatch)



@product.route("/tag/<int:tag_num>", methods=["GET", "POST"])
def product_tag(tag_num):
    tag_num=str(tag_num)
    tag_product = check_info("product_info", "tag", tag_num)
    if tag_product == None:
        return redirect(url_for('main.home')) # 태그에 저장된 것이 없을 경우  
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
        form = SubmitForm(request.form)
        email = session['email']
        if request.method == "POST" and form.validate():
            register_seller(email)
            flash(gettext('rg_seller'))
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
                flash( gettext('상품 정보가 수정되었습니다.'))
                return redirect(url_for('main.home'))
        if del_form.validate():
            delete_data("product_info", "product_n", product_str_n)
            flash(gettext('글이 삭제되었습니다.'))
            delete_data("user_cart", "product_id", product_str_n)
            return redirect(url_for('main.home'))
        else:
            return redirect(url_for('main.home'))
    else:
        return render_template("update_product.html", product_list=product_list, title="update", update_form=update_form, del_form=del_form)

