from flask_babel import gettext
from flask import Flask, render_template, url_for, flash, request, redirect, session, flash, send_from_directory, Blueprint
from shopping_website.main.routes import login_required
from shopping_website.forms import BoardForm, LocationForm, ProductForm, Submit_Form, Delete_Form
from shopping_website.db.db_functions import select_data, update_info, insert_data, insert_data1, insert_data2, insert_data3, update_data, update_location, delete_data, update_board
import gc
from shopping_website.db.dbconnect import connection
from MySQLdb import escape_string as thwart
import hashlib

board = Blueprint('board', __name__)

@board.route('/board_write', methods=["GET", "POST"])
@login_required
def board_page():
    #
    form = BoardForm(request.form)
    email = session['email']

    # Get user's information
    user_info = select_data(table_name="user_list", column1="email", row=str(email))
    user_id, username, password_db, email = user_info[0][0], user_info[0][1], user_info[0][2], user_info[0][3]

    # Write a new board
    if request.method == "POST" and form.validate():
        #
        title, content, pass_data = form.title.data, form.content.data, form.password.data
        password_input = hashlib.sha256(pass_data.encode()).hexdigest()
        # Check if an user is authorized
        if password_db == password_input:
            # save in DB
            insert_data2("board", title, content, email)   # insert_data2("board", title, content, user_id)
            flash(user_info[0][1] + gettext('님 빠른 시일 내에 연락드리겠습니다.'))
            return redirect(url_for('board.board_main'))
        else:
            # Wrong password
            flash( gettext('Wrong password') )
            return render_template("board_write.html", form=form, title="board_write")
    else:
        return render_template("board_write.html", form=form, username=username, title="board_write")


@board.route('/board', methods=["GET","POST"])
def board_main():
    # Get all of boards information
    board_list = select_data(table_name="board")
    n = len(board_list)

    # Get writer's email address
    email_list = []
    for i in range(n):
        user_email = board_list[i][3]
        email_list.append(user_email) # local

        #email = select_data(table_name="user_list", column1="uid", row=str(user_id), select_column="email")
        #email_list.append(email)

    return render_template("board_main.html", board_list=board_list, board_count_n=n, title="board", email=email_list)

@board.route("/board_update/<int:board_num>", methods=["GET", "POST"])
def board_update(board_num):
    # Get user's information
    email = session['email']
    board_n = str(board_num)
    user_info = select_data(table_name="user_list", column1="email", row=email)
    user_id, username, password_db, email = user_info[0][0], user_info[0][1], user_info[0][2], user_info[0][3]

    # Form
    del_form = Delete_Form(request.form)
    update_form = BoardForm(request.form)

    # Get a board_info
    board_list = select_data(table_name="board", column1="board_n", row=str(board_n))
    print(board_n)
    print(board_list)
    board_list = board_list[0] 

    # No authorization
    if board_list[3] != email: # local     # board_list[3] != user_id: -> server
        print(board_list[3], email)
        flash( gettext('권한 없음'))
        return redirect(url_for('board.board_main'))

    # Return a page to update or delete a board
    if request.method == "GET":
        return render_template("board_update.html", board_list=board_list,title="board_update", update_form=update_form, del_form=del_form)

    else:
        if request.method == "POST":

            # Update a board
            if update_form.validate():
                title, content, password, confirm  = update_form.title.data, update_form.content.data, update_form.password.data, update_form.confirm.data   # 사용자 - 보드 일치 확인 필요 (이메일로 들어가므로 불필요?)
                password_input = hashlib.sha256(password.encode()).hexdigest()

                # Wrong password
                if password_db != password_input:
                    flash( gettext('Wrong password') )
                    return redirect(url_for('board.board_main'))
                else:
                    update_board(board_n, title, content)
                    flash( gettext("수정되었습니다."))
                    return redirect(url_for('board.board_main'))

            # Delete a board
            if del_form.validate():
                delete_data("board", "board_n", board_n)
                flash(board_n + gettext('번 글 삭제되었습니다.'))
                return redirect(url_for('board.board_main'))

            else: # Fail to update or delete a board
                return render_template("board_update.html", board_list=board_list, title="board_update", update_form=update_form, del_form=del_form)



