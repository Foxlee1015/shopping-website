import os, hashlib, gc, urllib.request, secrets
from flask_babel import gettext
from PIL import Image
from flask import Flask, render_template, url_for, flash, request, redirect, session, flash, send_from_directory, Blueprint
from shopping_website.forms import ProductForm, Submit_Form, Delete_Form
from shopping_website.db.db_functions import select_data, update_info, insert_data, insert_data1, insert_data2, insert_data3, update_data, update_location, delete_data, insert_data6, check_cart
from wtforms import Form, PasswordField, validators, StringField, SubmitField, BooleanField
from shopping_website.db.dbconnect import connection
from MySQLdb import escape_string as thwart
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
from shopping_website.main.routes import login_required

product = Blueprint('product', __name__)

@product.context_processor
def context_processor():

    # Total products for Homepage
    product_list = select_data(table_name="product_info")
    n = len(product_list)
    categories = ['0', '여성패션', '남성패션', '뷰티', '식품', '주방용품', '생활용품' ,'홈인테리어', '가전디지털', '자동차', '완구취미', '문구', '도서']
    return dict(categories=categories, p_list=product_list, n=n) #, likes_count_all=likes_count_all)

@product.route('/register_product', methods=["GET", "POST"])
@login_required
def register_product():
    """
    파일이름 random_hex
    파일저장 후 insert_data1 상품 정보 저장
    """
    form = ProductForm(request.form)

    # Check if a user is a seller ( rank ==1 )
    email = session['email']
    user_id = select_data(table_name="user_list", column1="email", row=str(email))[0][0]
    rank = select_data(table_name="user_list", select_column="rank", column1="email", row=str(email))
    price = "50"


    # user is not a seller
    if rank[0][0] == None:
        flash( gettext('rg_seller'))
        return redirect(url_for('main.home'))

    if request.method == "POST" :
        product_name, product_intro, product_tag = form.product_name.data, form.product_intro.data, form.product_tag.data
        file = request.files['file'] 

        # NO file or No filename
        if not file or file.filename=="":
            flash( gettext('Upload a file or Check your file'))
            return render_template("register_product.html", form=form, title="register_product")

        # Save a new prouct information
        else:
            # Save a file
            random_hex = secrets.token_hex(8)
            filename = secure_filename(file.filename)
            filename =  random_hex + filename
            from run import app
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file.close()

            # Save in DB
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
    seller_id = select_data(table_name="product_info", select_column="user_id", column1="product_n", row=str(product_n)) 
    seller_info = select_data(table_name="user_list", column1="uid", row=seller_id[0][0])
    user_id, username = seller_info[0][0], seller_info[0][1]

    # Get likes info of a product
    get_likes = select_data(table_name="user_cart") #likes_info()
    u_idforproduct = [list[0] for list in get_likes if list[1] == product_n ]
    count_likes = len(u_idforproduct)

    # Buyer (Logged in) - Seller( Product's writer)
    buyer = select_data(table_name="user_list",select_column="uid", column1="email", row=email)[0][0]
    product_list = select_data(table_name="product_info", column1="product_n", row=str(product_n))
    seller = product_list[0][5]
    if buyer == seller :
        datamatch = True
    if buyer != seller :
        datamatch = False

    if request.method == "POST":
        p = check_cart("user_cart", "user_id", "product_id", str(buyer) ,str(product_n) )

        # A product is already in a cart
        if p:
            flash( gettext('already in a cart'))
            return redirect(url_for('main.home'))

        # Add a product in a cart
        else:
            insert_data6("user_cart", str(buyer), str(product_n))
            flash( gettext('added') )
            return  redirect(url_for('main.home'))
    # Return a products detail page
    else:
        product_list = select_data(table_name="product_info", column1="product_n", row=str(product_n))
        n = len(product_list)
        return render_template('product_list.html', product_detail=product_list[0], title="product_datails", datamatch=datamatch, likes=count_likes, username=username)

@product.route("/tag/<int:tag_num>", methods=["GET", "POST"])
def product_tag(tag_num):

    # Get a product whose tag is tag_num
    tag_num=str(tag_num)
    tag_product = select_data(table_name="product_info", column1="tag", row=tag_num)
    # No product whose tag is tag_num
    if tag_product == None:
        return redirect(url_for('main.home')) # 태그에 저장된 것이 없을 경우

    # Get a list of products
    product_list = tag_product
    n = len(product_list)
    x = select_data(table_name="user_cart")
    likes_count = []
    seller_list = []

    # likes, seller info
    for i in range(n):
        z = len([ item[0] for item in x if item[1] == product_list[i][0] ])
        likes_count.append(z)
        seller = select_data(table_name="user_list", column1="uid", row=str(product_list[i][5]))
        seller_list.append(seller[0][1])


    # Become a seller when logged in
    try:
        form = Submit_Form(request.form)
        email = session['email']
        if request.method == "POST" and form.validate():
            register_seller(email)
            flash(gettext('rg_seller'))
            rank = select_data(table_name="user_list", select_column="rank", column1="email", row=str(email))
            return render_template('home.html', p_list=product_list, n=n, likes_count_all=likes_count, rank=rank, tag_num=tag_num, seller=seller_list, count=likes_count)
        else:
            rank = select_data(table_name="user_list", select_column="rank", column1="email", row=str(email))
            return render_template('home.html', p_list=product_list, n=n, likes_count_all=likes_count, rank=rank, tag_num=tag_num, seller=seller_list, count=likes_count)

    # Not logged in
    except:
        rank = 0
        return render_template('home.html', p_list=product_list, n=n, likes_count_all=likes_count, rank=rank, tag_num=tag_num, seller=seller_list, count=likes_count)

@product.route("/product_update/<int:product_n>", methods=["GET", "POST"])
def product_update(product_n):

    #Form, Get a product information
    del_form = Delete_Form(request.form)
    update_form = ProductForm(request.form)
    product_num = str(product_n)
    product_list = select_data(table_name="product_info", column1="product_n", row=product_num)
    email = session['email']

    if request.method == "POST":

        # Update a product information
        if update_form.validate():
            product_name, product_intro, product_tag = update_form.product_name.data, update_form.product_intro.data, update_form.product_tag.data
            file = request.files['file']

            # No file or No filename
            if not file or file.filename == "":
                flash('Check your file')
                return redirect(url_for('main.home'))

            else:
                # Save a file
                random_hex = secrets.token_hex(8)
                filename = secure_filename(file.filename)
                filename = random_hex + filename
                from run import app
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # Update a product
                update_info("product_info", product_name, product_intro, filename, product_num)
                flash( gettext('상품 정보가 수정되었습니다.'))
                return redirect(url_for('main.home'))

        # Delete a product
        if del_form.validate():
            delete_data("product_info", "product_n", product_num)
            flash(gettext('글이 삭제되었습니다.'))
            return redirect(url_for('main.home'))

        else:
            return redirect(url_for('main.home'))

    #Get
    else:
        return render_template("update_product.html", product_list=product_list, title="update", update_form=update_form, del_form=del_form)

