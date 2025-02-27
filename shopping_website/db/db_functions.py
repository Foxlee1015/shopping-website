from shopping_website import mail
from shopping_website.db.dbconnect import connection
from MySQLdb import escape_string as thwart
from flask_mail import Message

def send_reset_email(email):
    msg = Message('Password reset request', sender='noreply@foxlee-shop.com', recipients=[email])
    msg.body = f''' To reset your pass, visit the following link:
http://127.0.0.1:5000/reset_pass/
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def db_input(*args):
    """
    :param args:
    :return: 들어간 정보 리스트로 반환
    """
    list = []
    for i in args:
        list.append(i)
    return list


def select_data(**kwargs):
    tablename= kwargs['table_name']
    c, conn = connection()
    c.execute("set names utf8")

    if 'select_column' in kwargs.keys() and 'row' in kwargs.keys():
        select_column, value, column1 = kwargs['select_column'], kwargs['row'], kwargs['column1']
        data = c.execute("SELECT "+ select_column +" FROM " + tablename +" WHERE " + column1 + " = (%s)", [value])

    elif 'row' in kwargs.keys():
        value, column1 = kwargs['row'], kwargs['column1']
        data = c.execute("SELECT * FROM " + tablename + " WHERE " + column1 + " = (%s)", [value])
    elif 'select_column' in kwargs.keys():
        select_column = kwargs['select_column']
        data = c.execute("SELECT "+ select_column +" FROM " + tablename +"")

    else:
        data = c.execute("SELECT * FROM " + tablename + "")
    info = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    return info


def check_cart(tablename, colname1, colname2, value1, value2):
    c, conn = connection()
    data = c.execute("SELECT * FROM "+tablename+" WHERE "+colname1+" = (%s) AND "+colname2+" = (%s)", [thwart(value1), thwart(value2)])
    list = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    return list


def order_info(user_id):
    c, conn = connection()
    c.execute("set names utf8")  # db 한글 있을 시 필요
    data = c.execute("SELECT p.order_id, p.product_number, o.user_id, o.time FROM order_products AS p LEFT JOIN user_order AS o ON p.order_id = o.order_id where user_id=(%s)", [thwart(user_id)])
    order_list = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    return order_list

def order_admin():
    c, conn = connection()
    c.execute("set names utf8")  # db 한글 있을 시 필요
    data = c.execute("SELECT u.uid, u.email, o.order_id, o.time FROM user_list AS u LEFT JOIN user_order AS o ON u.uid = o.user_id")
    info = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    if data :
        return info
    else:
        return None

def insert_data(table_name, value1, value2, value3):
    c, conn = connection()
    data = db_input(table_name, value1, value2, value3)
    c.execute("set names utf8")  # db에 한글 저장
    c.execute("INSERT INTO "+data[0]+" (username, password, email, points) VALUES (%s, %s, %s, %s)", [thwart(data[1]), thwart(data[2]), thwart(data[3]), thwart('10000')])
    conn.commit()
    c.close()
    conn.close()

def insert_data1(table_name, value1, value2, value3, value4, value5, value6):
    c, conn = connection()
    data = db_input(table_name, value1, value2, value3, value4, value5, value6)
    c.execute("set names utf8")  # db에 한글 저장
    c.execute("INSERT INTO "+data[0]+" (product_name, product_intro, filename, user_id, tag, price) VALUES (%s, %s, %s, %s, %s, %s)", [thwart(data[1]), thwart(data[2]), thwart(data[3]), thwart(data[4]), thwart(data[5]), thwart(data[6])])
    conn.commit()
    c.close()
    conn.close()

def insert_data2(table_name, value1, value2, value3):
    c, conn = connection()
    data = db_input(table_name, value1, value2, value3)
    c.execute("set names utf8")  # db에 한글 저장
    c.execute("INSERT INTO "+data[0]+" (title, content, email) VALUES (%s, %s, %s)", [thwart(data[1]), thwart(data[2]), thwart(data[3])])     # email -> user_id
    conn.commit()
    c.close()
    conn.close()

def insert_data3(user_id,address,zipcode,phonenumber):
    c, conn = connection()
    c.execute("set names utf8")  # 배송 정보 한글 저장.
    c.execute("INSERT INTO user_location (user_id, address, zipcode, phonenumber) VALUES (%s, %s, %s, %s)", [thwart(user_id), thwart(address), thwart(zipcode), thwart(phonenumber)])
    conn.commit()
    c.close()
    conn.close()


def insert_data4(user_id,time):
    c, conn = connection()
    c.execute("set names utf8")  # 배송 정보 한글 저장.
    c.execute("INSERT INTO user_order (user_id, time) VALUES (%s, %s)", [thwart(user_id), thwart(time)])
    conn.commit()
    c.close()
    conn.close()

def insert_data5(order_id,number):
    c, conn = connection()
    c.execute("set names utf8")  # 배송 정보 한글 저장.
    c.execute("INSERT INTO order_products (order_id, product_number) VALUES (%s, %s)", [thwart(order_id), thwart(number)])
    conn.commit()
    c.close()
    conn.close()

def insert_data6(tablename, col1, col2):
    c, conn = connection()
    data = db_input(tablename, col1, col2)
    c.execute("INSERT INTO "+data[0]+" VALUES (%s, %s)", [thwart(col1), thwart(col2)])
    conn.commit()
    c.close()
    conn.close()

def update_data(table_name, column_name, column_value, row_name, row_value):
    c, conn = connection()
    data = db_input(table_name, column_name, column_value, row_name, row_value)
    c.execute("set names utf8")  # db에 한글 저장
    c.execute("UPDATE "+data[0]+" SET "+data[1]+"=%s WHERE "+data[3]+"=%s", [thwart(data[2]), thwart(data[4])])
    conn.commit()
    c.close()
    conn.close()

def delete_data(table_name, column_name, column_value):
    c, conn = connection()  # 함수 추가
    data = db_input(table_name, column_name, column_value)
    c.execute("Delete FROM "+data[0]+" WHERE "+data[1]+"= (%s)", [thwart(data[2])])
    conn.commit()
    c.close()
    conn.close()

def update_location(address,zipcode,phonenumber,user_id):
    c, conn = connection()
    c.execute("set names utf8")  # 배송 정보 한글 저장.
    c.execute("UPDATE user_location SET address=(%s), zipcode=(%s), phonenumber=(%s)  WHERE email=(%s)", [thwart(address), thwart(zipcode), thwart(phonenumber), thwart(user_id)])
    conn.commit()
    c.close()
    conn.close()

def update_board(board_n,title,content):
    c, conn = connection()
    c.execute("set names utf8")  # 배송 정보 한글 저장.
    c.execute("UPDATE board SET title=(%s), content=(%s)  WHERE board_n=(%s)", [thwart(title), thwart(content), thwart(board_n)])
    conn.commit()
    c.close()
    conn.close()


def update_product(product_name,produc_intro,filename,username):
    c, conn = connection()
    data = db_input(product_name,produc_intro,filename,username)
    c.execute("set names utf8")  # 배송 정보 한글 저장.
    c.execute("UPDATE product_info SET product_name=(%s), product_intro=(%s), filename=(%s)  WHERE username=(%s)", [thwart(data[0]), thwart(data[1]), thwart(data[2]), thwart(data[3])])
    conn.commit()
    c.close()
    conn.close()


def update_info(tablename, product_name,product_intro,filename, product_n):
    c, conn = connection()
    data = db_input(tablename, product_name,product_intro,filename, product_n)
    c.execute("set names utf8")  # 배송 정보 한글 저장.
    c.execute("UPDATE "+data[0]+" SET product_name=(%s), product_intro=(%s), filename=(%s)  WHERE product_n=(%s)", [thwart(data[1]), thwart(data[2]), thwart(data[3]), thwart(data[4])])
    conn.commit()
    c.close()
    conn.close()


def update_info1(tablename, email, points):
    c, conn = connection()
    c.execute("set names utf8") 
    c.execute("UPDATE "+tablename+" SET points=(%s) WHERE email=(%s)", [thwart(points), thwart(email)])
    conn.commit()
    c.close()
    conn.close()

