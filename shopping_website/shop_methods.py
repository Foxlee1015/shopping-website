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

def db_input(*args):
    """
    :param args:
    :return: 들어간 정보 리스트로 반환
    """
    list = []
    for i in args:
        list.append(i)
    return list

def check_info(table_name, column, value):
    data = db_input(table_name, column, value)
    c, conn = connection()
    c.execute("set names utf8")  # db 한글 있을 시 필요
    data = c.execute("SELECT * FROM "+data[0]+" WHERE "+data[1]+" = (%s)", [thwart(data[2])])
    info_list = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    if data != 0:  # c.execute 로부터 해당 이메일이 존재하지 않으면 data == 0
        return info_list
    else:
        return None
# c.execute("SELECT * FROM board WHERE board_n = (%s)", [thwart(count_number)])
# check_info("board", "board_n", count_number)

def check_info2(row, table_name, column, value):           #이메일 입력 -> 비밀번호 출력
    c, conn = connection()
    data = db_input(row, table_name, column, value)
    c.execute("set names utf8")  # db 한글 있을 시 필요
    data = c.execute("SELECT "+data[0]+" FROM "+data[1]+" WHERE "+data[2]+" = (%s)", [thwart(data[3])])
    info2_list = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    if data != 0:  # c.execute 로부터 해당 이메일이 존재하지 않으면 data == 0
        return info2_list
    else:
        return None

def check_product(table_name):
    """
    테이블의 컬럼의 수 3개 이하인 경우 product_list[i][4] 에서 에러 발생 -> try, except 설정
    :return:
    """
    c, conn = connection()
    c.execute("set names utf8")  # db 한글 있을 시 필요
    table_name = table_name
    data = c.execute("SELECT * FROM "+table_name)
    product_list = c.fetchall()
    n = len(product_list)
    likes_count_all = []
    try:
        for i in range(n):
            x = product_list[i][4]
            if x != None:
                likes_count = x.count(',') + 1
                likes_count_all.append(likes_count)
            else:
                likes_count_all.append(0)
        return product_list, likes_count_all
    except:
        return product_list

def insert_data(table_name, value1, value2, value3):
    c, conn = connection()
    data = db_input(table_name, value1, value2, value3)
    c.execute("set names utf8")  # db에 한글 저장
    c.execute("INSERT INTO "+data[0]+" (username, password, email) VALUES (%s, %s, %s)", [thwart(data[1]), thwart(data[2]), thwart(data[3])])
    conn.commit()
    c.close()
    conn.close()

def insert_data1(table_name, value1, value2, value3, value4, value5):
    c, conn = connection()
    data = db_input(table_name, value1, value2, value3, value4, value5)
    c.execute("set names utf8")  # db에 한글 저장
    c.execute("INSERT INTO "+data[0]+" (product_name, product_intro, filename, username, tag) VALUES (%s, %s, %s, %s, %s)", [thwart(data[1]), thwart(data[2]), thwart(data[3]), thwart(data[4]), thwart(data[5])])
    conn.commit()
    c.close()
    conn.close()

def insert_data2(table_name, value1, value2, value3):
    c, conn = connection()
    data = db_input(table_name, value1, value2, value3)
    c.execute("set names utf8")  # db에 한글 저장
    c.execute("INSERT INTO "+data[0]+" (title, content, email) VALUES (%s, %s, %s)", [thwart(data[1]), thwart(data[2]), thwart(data[3])])
    conn.commit()
    c.close()
    conn.close()

def insert_data3(email,address,zipcode,phonenumber):
    c, conn = connection()
    c.execute("set names utf8")  # 배송 정보 한글 저장.
    c.execute("INSERT INTO user_location (email, address, zipcode, phonenumber) VALUES (%s, %s, %s, %s)", [thwart(email), thwart(address), thwart(zipcode), thwart(phonenumber)])
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

def update_location(address,zipcode,phonenumber,email):
    c, conn = connection()
    c.execute("set names utf8")  # 배송 정보 한글 저장.
    c.execute("UPDATE user_location SET address=(%s), zipcode=(%s), phonenumber=(%s)  WHERE email=(%s)", [thwart(address), thwart(zipcode), thwart(phonenumber), thwart(email)])
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

