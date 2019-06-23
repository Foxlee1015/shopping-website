from flask_babel import Babel, format_date, gettext
from flask import Flask, render_template, url_for, flash, request, redirect, session, flash, send_from_directory, Blueprint
from shopping_website import mail, babel
from shopping_website.main.main_functions import users_list
from shopping_website.db.db_functions import update_info, check_info, check_info2, insert_data, insert_data1, insert_data2, insert_data3, check_product, update_data, update_location, delete_data
from shopping_website.db.dbconnect import connection

admin = Blueprint('admin', __name__)

@admin.route('/admin/<string:category>')
def admin_category(category):
    orders_list = check_product("user_order")
    orders_count = len(orders_list)
    product_list, likes_count_all = check_product("product_info")
    user_list, likes = check_product("user_list")
    best_product_number = []
    x = likes_count_all
    for i in range(3):
        max_index =x.index( max(x))
        best_product_number.append(x[max_index])
        x[max_index]=0
    best_product = []
    for k in range(len(best_product_number)):
            best_product.append(product_list[best_product_number[k]])
    y = [['kr', 'us', 'jp'], [10, 20, 30]]
    product_count = len(product_list)+1
    user_count = len(user_list)+1
    ip_list=users_list()
    m = len(ip_list)
    return render_template('admin.html', m=m, ip_list=ip_list, y=y, p=best_product, l=likes_count_all, product_count=product_count, user_count=user_count, category=category, title=category, orders_list=orders_list, n=orders_count)


