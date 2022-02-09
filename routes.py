import secrets
import os
from PIL import Image
from flask import render_template, url_for, redirect, flash, request
from werkzeug.utils import secure_filename
from flaskapp import app, db, bcrypt
from flaskapp.forms import LoginForm, RegistrationForm, NewItemForm, NewProductForm, TYPE_CHOICES, FinalizeForm, TYPE_CHOICES2
from flaskapp.models import User, Item, Build, Product
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.is_submitted():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data, force=True)
            next_page = request.args.get('next')
            flash("Login Successful", 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You are now able to login!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn) 

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn  


@app.route("/new_item", methods=["GET", "POST"])
def new_item():
    form = NewItemForm()
    if form.validate_on_submit():
        if form.picture.data:
            price = round(int(form.price.data)/int(form.quantity.data), 2)
            picture_file = save_picture(form.picture.data)
            value = dict(TYPE_CHOICES).get(form.type.data)
            item = Item(name=form.name.data, price=price, parent_id=current_user.id , quantity=form.quantity.data, image_file=picture_file, type=value)
            db.session.add(item)
            db.session.commit()
            flash('Your item has been added to inventory!', 'success')
            return redirect(url_for('new_item'))
        price = round(int(form.price.data)/int(form.quantity.data), 2)
        item = Item(name=form.name.data, price=price, parent_id=current_user.id , quantity=form.quantity.data)
        db.session.add(item)
        db.session.commit()
        flash('Your item has been added to inventory!', 'success')
        return redirect(url_for('home'))
       

    return render_template('add_item.html', form=form)

def get_name(tup, dat):
     for i in tup:
            if dat in i:
                return i[1]



@app.route("/new_product", methods=["GET", "POST"])
def new_product():
    items = Item.query.all()
    build = Build.query.all()
    form = NewProductForm()
    form.item.choices = [(g.id, g.name) for g in Item.query.order_by(Item.name)]
    
    if form.is_submitted():
        value = get_name(form.item.choices, form.item.data)
        build_item = Build(item_pk=form.item.data, quantity=form.quantity.data, name=value)
        db.session.add(build_item)
        db.session.commit()
        flash(f'{str(form.quantity.data)} {value} has been added to the product build', 'success')
        return redirect(url_for('new_product'))
    return render_template('add_product.html', items=items, form=form, build=build)

@app.route("/finalize", methods=["GET", "POST"])
def finalize():
    form = FinalizeForm()
    build = Build.query.all()

    
    if form.is_submitted():
        if form.validate():
            if form.picture.data:
                value = dict(TYPE_CHOICES2).get(form.type.data)
                picture_file=save_picture(form.picture.data)
                item_list = {}
        
                for i in build:
                    item_list[Item.query.get(i.item_pk)]=i.quantity
        
                x = round(sum(k.price*v for k,v in item_list.items()), 2)
                components = ','.join(k.name +": " + str(v) for k, v in item_list.items())
            
                for i in item_list:
                    for l in build:
                        if i.name == l.name:
                            i.quantity = i.quantity - (l.quantity*form.quantity.data)
                            if i.quantity < 0:
                                flash(f'Unable to add due to insufficient amount of {i.name}', 'danger')
                                return redirect(url_for('finalize'))
                            db.session.commit()
                    


                product = Product(name=form.name.data, type=value, quantity=form.quantity.data, price=x, parent_id=current_user.id, image_file=picture_file, components=components)
                db.session.add(product)
                db.session.commit()
        
                Build.query.delete()
                db.session.commit()
                return redirect(url_for('new_product'))
            else:
                value = value = dict(TYPE_CHOICES2).get(form.type.data)
                item_list = {}
        
                for i in build:
                    item_list[Item.query.get(i.item_pk)]=i.quantity
        
           
                x = round(sum(k.price*v for k,v in item_list.items()), 2)
                components = ','.join(k.name +": " + str(v) for k, v in item_list.items())

                for i in item_list:
                    for l in build:
                        if i.name == l.name:
                            i.quantity = i.quantity - (l.quantity*form.quantity.data)
                            if i.quantity < 0:
                                flash(f'Unable to add due to insufficient amount of {i.name}', 'danger')
                                return redirect(url_for('finalize'))
                        
                            db.session.commit()
                    


                product = Product(name=form.name.data, type=value, quantity=form.quantity.data, price=x, parent_id=current_user.id, image_file=None)
                db.session.add(product)
                db.session.commit()

                Build.query.delete()
                db.session.commit()
                return redirect(url_for('new_product'))
         
    return render_template('finalize.html', form=form, build=build)


@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    items = Item.query.all()
    return render_template('home.html', items=items)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
def account():
    return render_template('account.html')

@app.route("/inventory")
def inventory():
    items = Item.query.all()
    return render_template('inventory.html', items=items)


@app.route("/item/<int:item_id>/update", methods=["GET", "POST"])
def update(item_id):
     item = Item.query.get_or_404(item_id)
     form = NewItemForm()
     if form.validate_on_submit():
        item.name = form.name.data
        item.quantity = form.quantity.data
        if form.picture.data:
            item.image_file = save_picture(form.picture.data)

        db.session.commit()
        flash('Your item has been updated!', 'success')
        return redirect(url_for('inventory'))
   
     return render_template('add_item.html', title='Update Item',
                           form=form, legend=f'Update {item.name}')

@app.route("/product/<int:product_id>/update", methods=["GET", "POST"])
def product(product_id):
     product = Product.query.get_or_404(product_id)
     form = FinalizeForm()
     components = product.components.split(",")
     if form.validate_on_submit():
        product.name = form.name.data
        product.quantity = form.quantity.data
        if form.picture.data:
            product.image_file = save_picture(form.picture.data)
        db.session.commit()
        flash('Your product has been updated!', 'success')
        return redirect(url_for('product_inventory'))
   
     return render_template('product.html', form=form, product=product, components=components)


@app.route("/item/<int:item_id>/delete", methods=["POST"])
def delete(item_id):
     item = Item.query.get_or_404(item_id)
     db.session.delete(item)
     db.session.commit()
     flash('The item has been deleted!', 'success')
     return redirect(url_for('home'))

@app.route("/product/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
     product = Product.query.get_or_404(product_id)
     db.session.delete(product)
     db.session.commit()
     flash('The item has been deleted!', 'success')
     return redirect(url_for('home'))

@app.route("/product_inventory")
def product_inventory():
    products = Product.query.all()
    return render_template('product_inventory.html', products=products)


@app.route("/build/<int:build_id>/delete", methods=["POST"])
def delete_build(build_id):
     build = Build.query.get_or_404(build_id)
     db.session.delete(build)
     db.session.commit()
     flash(f'{build.name} has been removed from build inventory', 'success')
     return redirect(url_for('new_product'))

@app.route("/item/<int:item_id>/", methods=["GET", "POST"])
def item(item_id):
     item = Item.query.get_or_404(item_id)
     form = NewItemForm()
     if form.is_submitted():
        item.name = form.name.data
        item.quantity = form.quantity.data
        if form.picture.data:
            item.image_file = save_picture(form.picture.data)
        db.session.commit()
        flash('Your item has been updated!', 'success')
        return redirect(url_for('inventory'))
   
     return render_template('item.html', item=item, form=form)
