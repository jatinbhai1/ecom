from flask import Flask,render_template, url_for, request,redirect, flash
from flask_bootstrap import Bootstrap
from forms import LoginForm,SignUp, AddProductCategory, AddProduct
import locale

from flask_login import LoginManager,UserMixin,login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash 
from authlib.integrations.flask_client import OAuth
from werkzeug.utils import secure_filename
import locale

def convert_to_rupees_string(number):
    locale.setlocale(locale.LC_NUMERIC, 'en_IN')  # Set the locale to Indian English
    rupees_string = locale.format_string("%.2f", number, grouping=True)
    return rupees_string

app = Flask(__name__)
Bootstrap(app)
oauth = OAuth(app)
oauth.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['UPLOADED_PHOTOS_DEST']='upload'
db = SQLAlchemy(app)
#here making login mangaer

app.secret_key="lsdjflksdjlkjewrlkjlkdsgjdsfsldkfjldskfjjas@#423jaimahak//|/?"

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
        return Users.query.get(int(user_id))





class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

class ProductCategory(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    product_category = db.Column(db.Integer, unique=True, nullable=False)

    img_loc=db.Column(db.String, unique=True, nullable=False)
    products = db.relationship('Product', backref='product_category')


class Product(db.Model):
    """this is a table that conatines all products with their categoy id"""
    id=db.Column(db.Integer, primary_key=True)
    pro_name = db.Column(db.String(100), nullable=False)

    product_description = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    formatted_price = db.Column(db.String, nullable=False)
    pro_img_loc= db.Column(db.String, nullable=False, unique=True)

    category_id = db.Column(db.Integer, db.ForeignKey('product_category.id'))




with app.app_context():
    db.create_all()

@app.route('/')
def home():

    if current_user.is_authenticated:
        style = "position: absolute;right: 60px;top: 10px;margin-top: 10px;"
    else:
        style = "position: absolute;right: 10px;top: 10px;margin-top: 10px;"

    product_category = db.session.query(ProductCategory).all()
    
    return render_template('index.html', is_logged_in=current_user.is_authenticated, style_of_ham=style, product_category=product_category)

@app.route('/add_cat', methods=['GET', 'POST'])
def add_product_category():
    form = AddProductCategory()
    if form.validate_on_submit():
        filename = secure_filename(form.image.data.filename)
        
        form.image.data.save('static/upload/'+filename)
        new_prod_cat= ProductCategory(product_category=form.product_name.data, img_loc=filename)
        try:
            db.session.add(new_prod_cat)
            db.session.commit()
            flash("Product category successfully added")
            return redirect(url_for('home'))
        except:
            flash('Product Category already exists')
            return redirect(url_for('add_product_category'))
    return render_template('add.html', form = form)
@app.route('/features')
def features():
    return render_template('features.html', is_logged_in=current_user.is_authenticated)
@app.route('/login', methods=['GET',"POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(Users).filter_by(email=form.email.data).first()
        if user:
            if user.email==form.email.data and check_password_hash(pwhash=user.password, password=form.password.data):
                login_user(user=user)
                flash('You have successfully logged in!')
                return redirect(url_for('home'))
            else:
                flash('Credentials not found please try to register with the given data')
                return redirect(url_for('sign_up'))
        else:
            flash('Credentials not found please try to register with the given data')
            return redirect(url_for('sign_up'))
    return render_template('login.html',form=form)

@app.route('/user-sign-up', methods=['GET','POST'])
def sign_up():
    form = SignUp()
    if form.validate_on_submit():
        new_user = Users(name=form.name.data, 
                          email=form.email.data, 
                          password=generate_password_hash(password=form.password.data, 
                                                          salt_length=10))
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            print(current_user)
            flash('You are successfully registered!')
            return redirect(url_for('home'))
        except:
            flash('The given email id is already registered log-in instead!')
            return redirect(url_for('login'))
        
    return render_template('signup.html', form=form)



@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/about-us')
def about_us():
    return render_template('about.html', is_logged_in=current_user.is_authenticated)

@app.route('/contact-us')
def contact():
    return render_template('contact.html', is_logged_in = current_user.is_authenticated)


@app.route('/add_pro', methods=['POST', 'GET'])
def add_product():
    all_category = [category.product_category for category in db.session.query(ProductCategory).all()]
    
    
    form = AddProduct()
    form.select_category.choices = all_category
    if form.validate_on_submit():
        price_in_rupee = convert_to_rupees_string(form.price.data)
        filename = secure_filename(form.product_image.data.filename)
        new_product = Product(pro_name=form.product_name.data,
                              product_description=form.product_description.data,
                              price = form.price.data,
                              pro_img_loc=filename,
                              formatted_price=price_in_rupee,
                              category_id=db.session.query(ProductCategory).filter_by(product_category = form.select_category.data).first().id)
        try:
            db.session.add(new_product)
            db.session.commit()
        except:
            flash('The given image is already present in database')
            redirect(url_for('add_product'))
        form.product_image.data.save('static/upload/'+filename)
        flash(f'Product successfully added to {form.select_category.data}')
        return redirect(url_for('home'))
    return render_template('add_product.html', form = form)





@app.route('/view-category/<int:id>')
def view_category(id):
    all_products_of_category = db.session.query(Product).filter_by(category_id = id).all()
    
    
    return render_template('all_products_of_cat.html', is_logged_in = current_user.is_authenticated, product_list = all_products_of_category)
    
if __name__ == "__main__":
    app.run(debug=True)