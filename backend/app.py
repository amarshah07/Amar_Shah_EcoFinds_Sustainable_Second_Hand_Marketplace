# backend/app.py
import re
import os
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from models import db, User, Product, Cart, Purchase
from sqlalchemy import or_

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devsecret')
    db.init_app(app)

    # ✅ Create tables at startup (Flask 3.x compatible)
    with app.app_context():
        db.create_all()

    return app

app = create_app()

# Predefined categories (used by forms)
CATEGORIES = ['Clothing', 'Electronics', 'Books', 'Furniture', 'Accessories', 'Other']

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

# ⚡ Removed @app.before_first_request (not needed anymore)

@app.route('/')
def feed():
    category = request.args.get('category')
    search = request.args.get('search')
    query = Product.query
    if category:
        query = query.filter(Product.category == category)
    if search:
        query = query.filter(Product.title.ilike(f'%{search}%'))
    products = query.order_by(Product.created_at.desc()).all()
    return render_template('feed.html', products=products, categories=CATEGORIES, selected_category=category, search=search)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        if not username or not email or not password:
            flash('All fields are required.', 'danger'); return redirect(url_for('register'))
        if not EMAIL_REGEX.match(email):
            flash('Invalid email format.', 'danger'); return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger'); return redirect(url_for('register'))
        pw_hash = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=pw_hash)
        db.session.add(user); db.session.commit()
        session['user_id'] = user.id
        flash('Registered and logged in.', 'success')
        return redirect(url_for('feed'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid credentials.', 'danger'); return redirect(url_for('login'))
        session['user_id'] = user.id
        flash('Logged in successfully.', 'success')
        return redirect(url_for('feed'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out.', 'info')
    return redirect(url_for('feed'))

@app.route('/product/add', methods=['GET','POST'])
@login_required
def add_product():
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        category = request.form.get('category')
        description = request.form.get('description','').strip()
        price_raw = request.form.get('price','0').strip()
        # validations
        if not title:
            flash('Title required.', 'danger'); return redirect(url_for('add_product'))
        try:
            price = Decimal(price_raw)
            if price < 0:
                raise Exception()
        except:
            flash('Invalid price.', 'danger'); return redirect(url_for('add_product'))
        if category not in CATEGORIES:
            category = 'Other'
        image_url = 'placeholder.png'  # placeholder approach for hackathon
        p = Product(user_id=session['user_id'], title=title, description=description, category=category, price=price, image_url=image_url)
        db.session.add(p); db.session.commit()
        flash('Product listed.', 'success')
        return redirect(url_for('feed'))
    return render_template('add_product.html', categories=CATEGORIES)

@app.route('/product/<int:pid>')
def product_detail(pid):
    p = Product.query.get_or_404(pid)
    return render_template('product_detail.html', product=p)

@app.route('/my-listings')
@login_required
def my_listings():
    products = Product.query.filter_by(user_id=session['user_id']).order_by(Product.created_at.desc()).all()
    
    # Fetch orders for each product
    products_with_orders = []
    for p in products:
        orders = Purchase.query.filter_by(product_id=p.id).order_by(Purchase.purchased_at.desc()).all()
        products_with_orders.append({'product': p, 'orders': orders})
    
    return render_template('my_listings.html', products_with_orders=products_with_orders)


@app.route('/product/<int:pid>/edit', methods=['GET','POST'])
@login_required
def edit_product(pid):
    p = Product.query.get_or_404(pid)
    if p.user_id != session['user_id']:
        flash('Not allowed.', 'danger'); return redirect(url_for('feed'))
    if request.method == 'POST':
        p.title = request.form.get('title','').strip()
        p.description = request.form.get('description','').strip()
        p.category = request.form.get('category', p.category)
        try:
            p.price = Decimal(request.form.get('price', p.price))
        except:
            flash('Invalid price'); return redirect(url_for('edit_product', pid=pid))
        db.session.commit()
        flash('Listing updated.', 'success'); return redirect(url_for('my_listings'))
    return render_template('add_product.html', edit=True, product=p, categories=CATEGORIES)

@app.route('/product/<int:pid>/delete', methods=['POST'])
@login_required
def delete_product(pid):
    p = Product.query.get_or_404(pid)
    if p.user_id != session['user_id']:
        flash('Not allowed.', 'danger'); return redirect(url_for('feed'))
    db.session.delete(p); db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('my_listings'))

@app.route('/cart/add/<int:pid>', methods=['POST'])
@login_required
def add_to_cart(pid):
    existing = Cart.query.filter_by(user_id=session['user_id'], product_id=pid).first()
    if existing:
        existing.quantity += 1
    else:
        c = Cart(user_id=session['user_id'], product_id=pid, quantity=1)
        db.session.add(c)
    db.session.commit()
    flash('Added to cart.', 'success')
    return redirect(request.referrer or url_for('feed'))

@app.route('/cart')
@login_required
def view_cart():
    items = Cart.query.filter_by(user_id=session['user_id']).all()
    # product info available via relationship
    return render_template('cart.html', items=items)

@app.route('/cart/remove/<int:cid>', methods=['POST'])
@login_required
def remove_cart(cid):
    it = Cart.query.get_or_404(cid)
    if it.user_id != session['user_id']:
        flash('Not allowed', 'danger'); return redirect(url_for('view_cart'))
    db.session.delete(it); db.session.commit()
    flash('Removed from cart', 'info'); return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()

    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('feed'))

    if request.method == 'POST':
        address = request.form.get('address')
        if not address:
            flash('Address is required!', 'danger')
            return redirect(url_for('checkout'))

        # create purchase record for each cart item
        for item in cart_items:
            purchase = Purchase(
                user_id=session['user_id'],
                product_id=item.product_id,
                address=address
            )
            db.session.add(purchase)

        # clear cart after checkout
        Cart.query.filter_by(user_id=session['user_id']).delete()
        db.session.commit()

        flash('Order placed successfully!', 'success')
        return redirect(url_for('purchases'))

    return render_template('checkout.html', items=cart_items)



@app.route('/purchases')
@login_required
def purchases():
    records = Purchase.query.filter_by(user_id=session['user_id']).order_by(Purchase.purchased_at.desc()).all()
    return render_template('purchases.html', records=records)

@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    user = User.query.get_or_404(session['user_id'])
    
    # Fetch all purchases of this user, newest first
    orders = Purchase.query.filter_by(user_id=user.id).order_by(Purchase.purchased_at.desc()).all()

    if request.method == 'POST':
        username = request.form.get('username','').strip()
        if not username:
            flash('Username cannot be empty', 'danger')
            return redirect(url_for('dashboard'))
        user.username = username
        db.session.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', user=user, orders=orders)


@app.route('/order/<int:purchase_id>/update', methods=['POST'])
@login_required
def update_order_status(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    
    # Only the owner of the product can update the order
    if purchase.product.user_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('my_listings'))
    
    status = request.form.get('status')
    if status:
        purchase.status = status  # we need to add this field in Purchase model
        db.session.commit()
        flash('Order status updated.', 'success')
    
    return redirect(url_for('my_listings'))


@app.route('/my-orders')
@login_required
def my_orders():
    # Fetch all purchases for the logged-in user, newest first
    purchases = Purchase.query.filter_by(user_id=session['user_id']).order_by(Purchase.purchased_at.desc()).all()
    return render_template('my_orders.html', purchases=purchases)





if __name__ == '__main__':
    app.run(debug=True)
