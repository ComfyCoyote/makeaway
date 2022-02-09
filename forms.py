from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, FloatField, SelectMultipleField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from flaskapp.models import User, Item

TYPE_CHOICES = [('1', 'beads'), ('2', 'findings'), ('3','chains/wires'), ('4', 'other'),('5', 'charm') ]
TYPE_CHOICES2 = [('1', 'necklace'), ('2', 'earring'), ('3', 'bracelet'), ('4', 'keychain'), ('5', 'phone charm'), ('6', 'hairclip'), ('7', 'other')] 


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired()])#need email validator
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField('Remember Me!')
    submit = SubmitField('Sign In!')

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired()])#needs email validator
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up!')

class NewItemForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=50)])
    price = FloatField("Price", validators=[DataRequired()])
    type = SelectField("Type", validators=[DataRequired()], choices=TYPE_CHOICES)
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    picture = FileField("Upload Picture?", validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    submit = SubmitField('Add Item')
    #image =

class NewProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=50)])
    item = SelectField("Items", validators=[DataRequired()], coerce=int)
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    picture = FileField("Upload Picture?", validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    submit_item = SubmitField('Add Item')
    finalize = SubmitField('Create Product')
    #image =

class FinalizeForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=50)])
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    type = SelectField("Jewelry Type",validators=[DataRequired()], choices=TYPE_CHOICES2 )
    picture = FileField("Upload Picture?", validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    submit_item = SubmitField('Add Product to Inventory')




    def validate_username(self, username):
       user = User.query.filter_by(username=username.data).first()
       if user:
           raise ValidationError("That username is taken, please choose another")


    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("That email is taken, please choose another")