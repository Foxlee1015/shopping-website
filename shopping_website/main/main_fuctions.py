import os
from shopping_website import mail
from shopping_website.db.dbconnect import connection
from MySQLdb import escape_string as thwart
from flask_mail import Message
from flask import request
from bs4 import BeautifulSoup
import urllib.request
from functools import wraps
import threading


def users_list():
    """
    현재 접속중인 IP 정보
    """
    a= os.popen('netstat -ant | grep ESTABLISHED | sort -u' ).read()
    a= a.replace('\n',' ')
    b = a.split(' ')
    c = []
    ip_list = []
    for x in range(len(b)):
        if b[x] != '':
            c.append(b[x])
    for y in range(len(c)):
        if (y+2) %6 == 0:
            m = c[y].index(':')
            if '127.0.0.1' not in c[y]:
                ip_list.append(c[y][:m])
    ip_list = list(set(ip_list))
    return ip_list

def send_reset_email(email):
    msg = Message('Password reset request', sender='noreply@foxlee-shop.com', recipients=[email])
    msg.body = f''' To reset your pass, visit the following link:
http://127.0.0.1:5000/reset_pass/
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash( gettext('You need to login first') )
            return redirect(url_for('main.login'))




def Get_ip_loca():
    ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    with urllib.request.urlopen("https://geoip-db.com/jsonp/"+ip) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        soup=str(soup)
        data = soup[9:-1]  # 딕셔너리로 변경하기 위해 불필요한 데이터 제거
        data = data.replace('null','None')
        data_dic = eval(data) # 딕셔너리로 변경
        return data_dic['country_name'], data_dic['state'], ip



def Get_product_location(product_n):
    with urllib.request.urlopen("https://service.epost.go.kr/trace.RetrieveDomRigiTraceList.comm?sid1="+product_n) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class':'table_col detail_off'})
        data = []
        for tr in table.find_all('tr'):
            tds = list(tr.find_all('td'))
            data_1 = []
            for td in tds:
                x = td.text
                x = x.replace("\n", "")
                x = x.replace("\t", "")
                x = x.replace("\xa0", "")
                x = x.replace(" ", "")
                data_1.append(x)
            data.append(data_1)
        return data
