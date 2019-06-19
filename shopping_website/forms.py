from wtforms import Form, PasswordField, validators, StringField, SubmitField, TextAreaField, FileField, BooleanField, SelectField
from flask_wtf.file import FileAllowed, FileRequired
from flask_babel import gettext, lazy_gettext

class LoginForm(Form):
    email = TextAreaField('Email Address', [validators.data_required(), validators.Length(min=1, max=50)])
    password = PasswordField('Password', [validators.data_required()])
    submit = SubmitField('Login')

class RegistrationForm(Form):
    username = TextAreaField('Username', [validators.data_required(), validators.Length(min=1, max=20)])
    email = TextAreaField('Email Address', [validators.Length(min=1, max=50)])
    password = PasswordField('Password', [validators.data_required(),
                                          validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Register')

class RequestResetForm(Form):
    email = StringField('Email Address', [validators.Length(min=1, max=50)])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(Form):
    email = StringField('Email Address', [validators.Length(min=1, max=50)])
    password = PasswordField('New Password', [validators.data_required(), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Reset Password')

class BoardForm(Form):
    title = TextAreaField('Title', [validators.Length(min=1, max=20)])
    content = TextAreaField('Content', [validators.Length(min=1, max=500)])
    password = PasswordField('Password', [validators.data_required(),
                                          validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('ok')

class LocationForm(Form):
    address = StringField('Address', [validators.Length(min=1, max=20)])
    zipcode = StringField('Zipcode', [validators.Length(min=1, max=20)])
    phonenumber = StringField('Phonenumber', [validators.Length(min=10, max=13)])
    submit = SubmitField('ok')

a = lazy_gettext('female')
b = lazy_gettext('male')
c = lazy_gettext('beauty')
d = lazy_gettext('food')
e = lazy_gettext('kitchen')
f = lazy_gettext('home tools')
g = lazy_gettext('home design')
h = lazy_gettext('device')
i = lazy_gettext('car')
j = lazy_gettext('hobby')
k = lazy_gettext('stationary')
l = lazy_gettext('book')

class ProductForm(Form):
    product_name = TextAreaField('Product Name', [validators.data_required(),validators.Length(min=1, max=20)])
    product_tag = SelectField('Product Tag', choices=[('1',a), ('2',b), ('3',c), ('4',d), ('5',e), ('6',f), ('7',g), ('8',h), ('9',i), ('10',j), ('11',k), ('12',l) ])
    product_intro = TextAreaField('Product Intro', [validators.data_required(), validators.Length(min=1, max=50)])
    product_pic = FileField('Product picture', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('okay')

class Delete_Form(Form):
    accept = BooleanField('I agree to delete this.', [validators.data_required()])
    submit1 = SubmitField('삭제')

class Submit_Form(Form):
    submit = SubmitField('Okay')

class Location_track_Form(Form):
    submit = SubmitField('배송조회')
