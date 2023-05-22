from wtforms import StringField, PasswordField, SubmitField,EmailField, FileField, IntegerField, SelectField,BooleanField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_wtf.file import FileField


class LoginForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()], id='password')
    
    submit = SubmitField(label="Log-in")

class SignUp(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    email = EmailField(label="Email", validators=[DataRequired()])
    password= PasswordField(label='Password', validators=[DataRequired()], id='password')
    
    submit = SubmitField(label="Sign-up")

class AddProductCategory(FlaskForm):
    product_name = StringField(label="Product Name", validators=[DataRequired()])
    image = FileField(label="Upload a image")
    submit = SubmitField(label='Add Category')


class AddProduct(FlaskForm):
    product_name = StringField(label='Product Name', validators=[DataRequired()])
    select_category = SelectField(label='Select Category',validators=[DataRequired()])
    product_description = StringField(label='Description', validators=[DataRequired()])
    price = IntegerField(label='Price', validators=[DataRequired()])
    product_image = FileField(label='Upload Image', id='Form-Control')
   
    submit = SubmitField(label='Add Product')
    
   
    
