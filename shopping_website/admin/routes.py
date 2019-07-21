import json
import operator
from flask_babel import Babel, format_date, gettext
from flask import Flask, render_template, url_for, flash, request, redirect, session, flash, send_from_directory, Blueprint
from shopping_website import mail, babel
from shopping_website.main.main_functions import users_list, manage_memory
from shopping_website.db.db_functions import update_info, insert_data, insert_data1, insert_data2, insert_data3, update_data, update_location, delete_data, order_admin
from shopping_website.db.dbconnect import connection

admin = Blueprint('admin', __name__)

@admin.route('/admin/<string:category>')
def admin_category(category):
    # Memory usage
    used_data, avail_data = manage_memory()
    y = [['Used', 'Available'], [float(used_data[:-1]), float(avail_data[:-1])]]

    # Order information
    orders_list = order_admin()
    orders_count = len(orders_list)

    # Product information
    product_list = select_data(table_name="product_info")
    product_count = len(product_list)+1

    # User information
    user_list = select_data(table_name="user_list")
    user_count = len(user_list)+1

    # Connected users
    ip_list=users_list()
    m = len(ip_list)

    # TOP 3 products // Each product's likes | sort |
    z = select_data(table_name="user_cart")
    likes_count=[]
    for i in range(len(product_list)):
        k = len( [ item[0] for item in z if item[1] == product_list[i][0] ] )
        likes_count.append([product_list[i][0], k])
    likes_count = sorted(likes_count, key=operator.itemgetter(1), reverse=True)
    top3_products = []
    for k in range(3):
        top3_products.append(product_list[likes_count[k][0]])

    return render_template('admin.html', m=m, ip_list=ip_list, y=y, p=top3_products, l=likes_count, product_count=product_count, user_count=user_count, category=category, title=category, orders_list=orders_list, n=orders_count, used_data=used_data, avail_data=avail_data)
