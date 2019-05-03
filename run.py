from flask import Flask, render_template, url_for, flash, request, redirect, session, flash
from wtforms import Form, BooleanField, PasswordField, validators, StringField, SubmitField
from flask_mail import Mail
from dbconnect import connection
from MySQLdb import escape_string as thwart
from flask_login import login_user, current_user, logout_user, login_required, LoginManager
import hashlib
import gc
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@app.route("/")
@app.route("/home")
def home():
        return render_template('home.html')

class LoginForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [validators.data_required()])
    submit = SubmitField('Login')

@app.route('/login/', methods=["GET", "POST"])
def login():
    #error = ''
    try:
        if session['logged_in'] == True:       # 로그인 상태에서는 홈으로
            return redirect(url_for('home'))
    except:          # 세션에서 오류뜰때 except = 로그인 되지 않은 상태면 log 페이지로 이동
            form = LoginForm(request.form)
            c, conn = connection()
            if request.method == "POST" and form.validate():
                email = form.email.data
                data = c.execute("SELECT * FROM user_list WHERE email = (%s)", [thwart(email)])
                if data == 0:  # c.execute 로부터 해당 이메일이 존재하지 않으면 data == 0
                    flash('This email doesnt exist')
                    return render_template("login.html")

                data1 = c.fetchone()[2]  # 테이블에서 비밀번호 가져오기
                c.execute("set names utf8")  # db에서 닉네임 가져오기 전(한글 닉네임)
                data_user = c.execute("SELECT username FROM user_list WHERE email = (%s)", [thwart(email)])
                data2 = c.fetchone()[0] # 테이블에서 해당 이메일의 username 가져오기

                if data != 0:   # data 해당 email이 존재하고
                    pass_data = form.password.data  # 암호화 필요
                    password = hashlib.sha256(pass_data.encode()).hexdigest()
                    if data1 == password:  # 테이블에서 가져온 비번과 loginform의 비밀번호의 데이터악 일치하면   암호화 필요! sha256_crypt.verify(form.password, data):
                        session['logged_in'] = True
                        session['email'] = request.form['email']
                        flash(data2 + "님 즐거운 쇼핑 되십시오. You are now logged in")
                        return render_template("home.html", username=data2)
                    if data1 != form.password.data:
                        flash('Wrong password')
                        return render_template("login.html") # error=error
            #gc.collect()
            return render_template("login.html", form=form)
    #except Exception as e:
    #    flash(e)
    #    flash("Invalid credentials, try again.")
    #    return render_template("login.html", error=error)

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [validators.data_required(), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    #accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)', [validators.data_required()])
    submit = SubmitField('Register')

@app.route('/register/', methods=["GET", "POST"])
def register_page():
    try:
        if session['logged_in'] == True:
            return redirect(url_for('home'))
    except:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            pass_data = form.password.data  #암호화 필요
            password = hashlib.sha256(pass_data.encode()).hexdigest()
            c, conn = connection()

            x = c.execute("SELECT * FROM user_list WHERE username = (%s)",
                          [thwart(username)])
            y = c.execute("SELECT * FROM user_list WHERE email = (%s)",
                          [thwart(email)])
            if int(x) > 0 :
                flash("That username is already taken, please choose another")
                return render_template('register_test.html', form=form)
            if int(y) > 0:
                flash("That email is already taken, please choose another")
                return render_template('register_test.html', form=form)

            else:
                c.execute("set names utf8") # db에 한글 저장
                c.execute("INSERT INTO user_list (username, password, email, tracking) VALUES (%s, %s, %s, %s)",
                          (thwart(username), thwart(password), thwart(email),
                           thwart("/introduction-to-python-programming/")))

                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('home'))
        flash("Type the info")
        return render_template("register_test.html", form=form)

    #except Exception as e:
    #    print(str(e))
    #    return (str(e))

class RequestResetForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=50)])
    submit = SubmitField('Request Password Reset')

@app.route("/reset/", methods=["GET", "POST"])
def reset():
    #if session['logged_in'] == True:       # 로그인 상태에서는 홈으로
    #    return redirect(url_for('home'))
    form = RequestResetForm(request.form)
    c, conn = connection()
    if request.method == "POST":
        email = form.email.data
        data = c.execute("SELECT * FROM user_list WHERE email = (%s)", [thwart(email)])
        if data == 0:  # c.execute 로부터 해당 이메일이 존재하지 않으면 data == 0
            flash('This email doesnt exist')
            return render_template("reset.html", form=form)
        else:
            flash('Please check your email')
            return render_template("reset_pass.html")
    else: # POST 가 아닌 GET 인 경우 reset 페이지로 가서 email 넣고 post
        return render_template("reset.html")

class ResetPasswordForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [validators.data_required(), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Reset Password')

@app.route("/reset_pass/", methods=["GET", "POST"])
def reset_pass():
    #if session['logged_in'] == True:       # 로그인 상태에서는 홈으로
    #    return redirect(url_for('home'))
    form = ResetPasswordForm(request.form)
    c, conn = connection()
    if request.method == "POST":
        email = form.email.data
        password = form.password.data
        confirm = form.confirm.data
        if password != confirm:
            flash('Check your password')
            return render_template("reset_pass.html", form=form)
        data = c.execute("SELECT * FROM user_list WHERE email = (%s)", [thwart(email)])
        if data == 0:  # c.execute 로부터 해당 이메일이 존재하지 않으면 data == 0
            flash('This email doesnt exist')
            return render_template("reset_pass.html", form=form)

        else:
            change_pass = c.execute("UPDATE user_list SET password = (%s) WHERE email = (%s)", [thwart(password), thwart(email)])
            conn.commit()  # 업데이트한 후 반드시 필요!
            flash('Success')
            print('11')
            return redirect(url_for('login'))  # 비번 바꾼후 login 으로 이동
    else: # POST 가 아닌 GET 인 경우 reset 페이지로 가서 email 넣고 post
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

class BoardForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=20)])
    content = StringField('Content', [validators.Length(min=10, max=50)])
    password = PasswordField('Password', [validators.data_required(), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('ok')

@app.route('/board_write', methods=["GET", "POST"])
def board_page():
    try:
        if session['logged_in'] != True:
            return redirect(url_for('login'))
        email = session['email']
        form = BoardForm(request.form)
        if request.method == "POST" and form.validate():
            title = form.title.data
            content = form.content.data
            #password = form.password.data  #암호화 필요
            c, conn = connection()
            data = c.execute("SELECT * FROM user_list WHERE email = (%s)", [thwart(email)]) # 이메일 존재하는지 먼저 확인
            if data == 0:  # c.execute 로부터 해당 이메일이 존재하지 않으면 data == 0
                flash('This email doesnt exist')
                return render_template("login.html")
            data1 = c.fetchone()[2]  # 테이블에서 비밀번호 가져오기
            data_user = c.execute("SELECT username FROM user_list WHERE email = (%s)", [thwart(email)])
            data2 = c.fetchone()[0]  # 테이블에서 해당 이메일의 username 가져오기

            if data != 0:  # data 해당 email이 존재하고
                pass_data = form.password.data  # 암호화 필요
                password = hashlib.sha256(pass_data.encode()).hexdigest()
                if data1 == password:  # 테이블에서 가져온 비번과 loginform의 비밀번호의 데이터와 일치하면   암호화 필요! sha256_crypt.verify(form.password, data):
                    c.execute("set names utf8")  # db 한글 저장
                    c.execute("INSERT INTO board (title, content, email) VALUES (%s, %s, %s)", (thwart(title), thwart(content), thwart(email)))
                    conn.commit()
                    flash(data2 + "님 빠른 시일 내에 연락드리겠습니다.")
                    c.close()
                    conn.close()
                    gc.collect()
                    return redirect(url_for('home'))
                if data1 != form.password.data:
                    flash('Wrong password')
                    return render_template("board_write.html", form=form)
        else:
            return render_template("board_write.html", form=form, email=email)
    except Exception as e:
        return render_template("board_write.html", form=form)

@app.route('/board', methods=["GET","POST"])
def board_main():
    c, conn = connection()
    board_count = c.execute("SELECT board_n FROM board")                           # 게시된 글의 수.
    board_count_number = board_count                                               # board_count_number 수 저장
    board_n_list = c.fetchall()                                                   # c.exectue 에서 게시판의 넘버 정보 가져오기
    board_list = [[None for k in range(4)] for j in range(board_count_number)]    # 갯수에 맞춰 데이터가 들어갈 2차 행렬
    for x in range(board_count_number):                                            # 게시글의 수 loop
        count_number = str(board_n_list[x][0])                                     # 튜플에 저장된 게실글의 넘버만 가져와서 문자열로( thart에 들어갈 문자열 )   board_n_list = ((1,),(2,),(3,),(6,)) 처럼 저장됨
        for i in range(4):                                                         # i 0~3 (보드넘버, 제목, 내용, 이메일)
            c.execute("set names utf8")                                            # 한글 데이터
            board_data = c.execute("SELECT * FROM board WHERE board_n = (%s)", [thwart(count_number)])  # count_number = 게시글의 넘버 // 보드 넘버를 기준으로 보드넘버, 제목, 내용, 이메일 가져옴
            board_data1 = c.fetchone()[i]
            board_list[x][i] = board_data1                                         # 가져온 데이터 리스트에 저장
    print(board_list)
    return render_template("board_main.html", board_list=board_list, board_count_n=board_count_number)

class LocationForm(Form):
    address = StringField('Address', [validators.Length(min=1, max=20)])
    zipcode = StringField('Zipcode', [validators.Length(min=1, max=20)])
    phonenumber = StringField('Phonenumber', [validators.Length(min=10, max=13)])
    submit = SubmitField('ok')

@app.route('/mypage', methods=["GET", "POST"])
def my_page():
    try:
        if session['logged_in'] != True:
            return redirect(url_for('login'))
        form = LocationForm(request.form)
        email = session['email']          #로그인된 상태에서의 이메일 정보 가져와서 db에 아래 정보와 같이 저장
        if request.method == "POST" and form.validate():
            address = form.address.data
            zipcode = form.zipcode.data
            phonenumber = form.phonenumber.data
            c, conn = connection()
            c.execute("INSERT INTO user_location (email, address, zipcode, phonenumber) VALUES (%s, %s, %s, %s)", (thwart(email), thwart(address), thwart(zipcode), thwart(phonenumber)))
            conn.commit()
            flash(" 소중한 정보 감사합니다.")
            c.close()
            gc.collect()
            return render_template("home.html", form=form)
            #return render_template("mypage.html", form=form)
        else:                                                        # 로그인된 상태에서 email 정보 가져오고, 이 메일을 기반으로 저장된 데이터를 가져와서 빈칸에 넣는다.
            c, conn = connection()
            data = c.execute("SELECT * FROM user_location WHERE email = (%s)", [thwart(email)])
            if data != 0:
                c.execute("set names utf8")
                location_data = c.execute("SELECT * FROM user_location WHERE email = (%s)", [thwart(email)])
                location_data_all = c.fetchall()
                print(location_data_all)
                return render_template("mypage.html", form=form, location_data_all=location_data_all)
            else:
                location_data_all = ((""),(""),(""),(""),)   # data == 0 인 경우에는 db에 location data 가 없으므로 빈 행렬로 html 에 빈칸으로 출력
                return render_template("mypage.html", form=form, location_data_all=location_data_all)
    except Exception as e:
        return render_template("mypage.html", form=form)

if __name__ == '__main__':
    app.run(debug=True)
