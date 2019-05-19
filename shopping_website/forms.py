from wtforms import Form, PasswordField, validators, StringField, SubmitField, TextAreaField, FileField
from flask_wtf.file import FileAllowed, FileRequired

class LoginForm(Form):
    email = TextAreaField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.data_required()])
    submit = SubmitField('Login')

class RegistrationForm(Form):
    username = TextAreaField('Username', [validators.Length(min=4, max=20)])
    email = TextAreaField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.data_required(),
                                          validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Register')

class RequestResetForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=50)])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [validators.data_required(), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Reset Password')

class BoardForm(Form):
    title = TextAreaField('Title', [validators.Length(min=1, max=20)])
    content = TextAreaField('Content', [validators.Length(min=10, max=50)])
    password = PasswordField('Password', [validators.data_required(),
                                          validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('ok')

class Update_Form(Form):
    title = TextAreaField('Title', [validators.Length(min=1, max=20)])
    content = TextAreaField('Content', [validators.Length(min=10, max=50)])
    password = PasswordField('Password', [validators.data_required(),
                                          validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('ok')

class LocationForm(Form):
    address = StringField('Address', [validators.Length(min=1, max=20)])
    zipcode = StringField('Zipcode', [validators.Length(min=1, max=20)])
    phonenumber = StringField('Phonenumber', [validators.Length(min=10, max=13)])
    submit = SubmitField('ok')

class ProductForm(Form):
    product_name = TextAreaField('Product Name', [validators.Length(min=1, max=20)])
    product_intro = TextAreaField('Product Intro', [validators.Length(min=10, max=50)])
    product_pic = FileField('Product picture', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('okay')

class LikesForm(Form):
    submit = SubmitField('장바구니')

class Register_seller_Form(Form):
    submit = SubmitField('판매자등록')

class Buy_Form(Form):
    submit = SubmitField('구매하기')

class Location_track_Form(Form):
    submit = SubmitField('배송조회')

class Delete_Form(Form):
    submit = SubmitField('배송조회')