from shopping_website import app, mail
from shopping_website.dbconnect import connection
from MySQLdb import escape_string as thwart
from flask_mail import Message

def send_reset_email(email):
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
    c.execute("INSERT INTO user_list (username, password, email) VALUES (%s, %s, %s)", [thwart(username), thwart(password), thwart(email)])
    conn.commit()
    c.close()
    conn.close()

def insert_data_board(title, content, email):
    c, conn = connection()
    c.execute("set names utf8")  # db 한글 저장
    c.execute("INSERT INTO board (title, content, email) VALUES (%s, %s, %s)", [thwart(title), thwart(content), thwart(email)])
    conn.commit()
    c.close()
    conn.close()

def check_product():
    c, conn = connection()
    c.execute("set names utf8")  # db 한글 있을 시 필요
    data = c.execute("SELECT * FROM product_info")
    product_list = c.fetchall()
    return product_list

def insert_data_product(product_name, product_intro, filename):
    c, conn = connection()
    c.execute("set names utf8")
    c.execute("INSERT INTO product_info (product_name, product_intro, filename) VALUES (%s, %s, %s)", [thwart(product_name), thwart(product_intro), thwart(filename)])
    conn.commit()
    c.close()
    conn.close()


def check_likesinfo(email):           #이메일 입력 -> 비밀번호 출력
    c, conn = connection()
    c.execute("set names utf8")  # db 한글 있을 시 필요
    data = c.execute("SELECT likes FROM user_list WHERE email = (%s)", [thwart(email)])
    likes_list = c.fetchall()
    if data == 0:  # c.execute 로부터 해당 이메일이 존재하지 않으면 data == 0
        return None
    else:
        return likes_list

def get_product_info(product_n):
    c, conn = connection()
    c.execute("set names utf8")  # db 한글 있을 시 필요
    data = c.execute("SELECT * FROM product_info WHERE product_n = (%s)", [thwart(product_n)])
    product_list = c.fetchall()
    return product_list

def update_location(address,zipcode,phonenumber,email):
    c, conn = connection()
    c.execute("set names utf8")  # 배송 정보 한글 저장.
    c.execute("UPDATE user_location SET address=(%s), zipcode=(%s), phonenumber=(%s)  WHERE email=(%s)", [thwart(address), thwart(zipcode), thwart(phonenumber), thwart(email)])
    conn.commit()
    c.close()
    conn.close()

def insert_location(email,address,zipcode,phonenumber):
    c, conn = connection()
    c.execute("set names utf8")  # 배송 정보 한글 저장.
    c.execute("INSERT INTO user_location (email, address, zipcode, phonenumber) VALUES (%s, %s, %s, %s)", [thwart(email), thwart(address), thwart(zipcode), thwart(phonenumber)])
    conn.commit()
    c.close()
    conn.close()

def show_current_location(email):
    c, conn = connection()
    c.execute("set names utf8")
    c.execute("SELECT * FROM user_location WHERE email=(%s)", [thwart(email)])
    location_data_all = c.fetchall()
    return location_data_all

def update_likes_product(product_n,email):
    c, conn = connection()
    c.execute("set names utf8")  # db에 한글 저장
    c.execute("UPDATE user_list SET likes=%s WHERE email=%s", (thwart(product_n), thwart(email)))
    conn.commit()
    c.close()
    conn.close()

def update_1st_like(new_list,email):
    c, conn = connection()
    c.execute("set names utf8")  # db에 한글 저장
    c.execute("UPDATE user_list SET likes=%s WHERE email=%s", (thwart(new_list), thwart(email)))
    conn.commit()
    c.close()
    conn.close()
