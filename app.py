"""
AV Brands - Main Flask Application
E-commerce website for clothing shop with full functionality
"""
import os
import json
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, FloatField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange

from config import config
from models import db, User, Category, Product, CartItem, WishlistItem, Order, OrderItem, Offer, Comment, RecentlyViewed

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['default'])

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

# ============ FORMS ============

class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=20)])

class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class ProfileForm(FlaskForm):
    """User profile update form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    city = StringField('City', validators=[Optional()])
    state = StringField('State', validators=[Optional()])
    pincode = StringField('Pincode', validators=[Optional()])

class ProductForm(FlaskForm):
    """Product management form"""
    name = StringField('Product Name (English)', validators=[DataRequired()])
    name_kannada = StringField('Product Name (Kannada)', validators=[Optional()])
    description = TextAreaField('Description (English)', validators=[Optional()])
    description_kannada = TextAreaField('Description (Kannada)', validators=[Optional()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    discount_price = FloatField('Discount Price', validators=[Optional(), NumberRange(min=0)])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    sizes = StringField('Sizes (comma separated)', validators=[Optional()])
    colors = StringField('Colors (comma separated)', validators=[Optional()])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    is_featured = BooleanField('Featured Product')
    is_active = BooleanField('Active')

class OfferForm(FlaskForm):
    """Offer management form"""
    title = StringField('Title (English)', validators=[DataRequired()])
    title_kannada = StringField('Title (Kannada)', validators=[Optional()])
    description = TextAreaField('Description (English)', validators=[Optional()])
    description_kannada = TextAreaField('Description (Kannada)', validators=[Optional()])
    discount_percentage = FloatField('Discount Percentage', validators=[DataRequired(), NumberRange(min=0, max=100)])
    product = SelectField('Product', coerce=int, validators=[Optional()])
    is_active = BooleanField('Active')

class CommentForm(FlaskForm):
    """Comment/suggestion form"""
    comment_type = SelectField('Type', choices=[('request', 'Request New Product'), ('suggestion', 'Suggestion'), ('feedback', 'Feedback')], validators=[DataRequired()])
    subject = StringField('Subject', validators=[Optional(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])

class CheckoutForm(FlaskForm):
    """Checkout form"""
    shipping_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    shipping_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    shipping_address = TextAreaField('Address', validators=[DataRequired()])
    shipping_city = StringField('City', validators=[DataRequired(), Length(max=100)])
    shipping_state = StringField('State', validators=[DataRequired(), Length(max=100)])
    shipping_pincode = StringField('Pincode', validators=[DataRequired(), Length(max=10)])
    payment_method = SelectField('Payment Method', choices=[('cod', 'Cash on Delivery'), ('card', 'Card Payment')], validators=[DataRequired()])

# ============ HELPERS ============

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def get_cart_count():
    """Get total items in cart"""
    if current_user.is_authenticated:
        return CartItem.query.filter_by(user_id=current_user.id).count()
    return 0

def get_cart_total():
    """Get total price of cart items"""
    if current_user.is_authenticated:
        items = CartItem.query.filter_by(user_id=current_user.id).all()
        total = sum(item.get_total_price() for item in items)
        return total
    return 0

def get_recently_viewed():
    """Get recently viewed products"""
    if current_user.is_authenticated:
        viewed = RecentlyViewed.query.filter_by(user_id=current_user.id).order_by(RecentlyViewed.viewed_at.desc()).limit(8).all()
        return [v.product for v in viewed if v.product and v.product.is_active]
    return []

# Make helpers available in templates
app.jinja_env.globals.update(get_cart_count=get_cart_count, get_cart_total=get_cart_total, get_recently_viewed=get_recently_viewed)

# ============ LANGUAGE ROUTES ============

@app.route('/set_language/<lang>')
def set_language(lang):
    """Set language preference"""
    if lang in ['en', 'kn']:
        session['language'] = lang
    return redirect(request.referrer or url_for('index'))

# ============ PUBLIC ROUTES ============

@app.route('/')
def index():
    """Home page"""
    lang = session.get('language', 'en')
    featured_products = Product.query.filter_by(is_active=True, is_featured=True).limit(8).all()
    trending_products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(8).all()
    active_offers = Offer.query.filter_by(is_active=True).all()
    active_offers = [o for o in active_offers if o.is_valid()]
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('index.html', 
                         featured_products=featured_products,
                         trending_products=trending_products,
                         active_offers=active_offers,
                         categories=categories,
                         lang=lang)


@app.route('/__ping')
def _ping():
    """Lightweight healthcheck to verify server responsiveness."""
    return 'ok', 200


@app.route('/gallery')
def gallery():
    """Aesthetic gallery / lookbook page showing clothing photos."""
    lang = session.get('language', 'en')
    # Collect images from the static/images folder. Place your images there.
    images = [
        'photo-1567401893414-76b7b1e5a7a5.avif',
    ]
    return render_template('gallery.html', images=images, lang=lang)

@app.route('/shop')
@app.route('/shop/<category_slug>')
def shop(category_slug=None):
    """Shop page with products and filters"""
    lang = session.get('language', 'en')
    category = request.args.get('category', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    size = request.args.get('size')
    color = request.args.get('color')
    sort = request.args.get('sort', 'newest')
    search = request.args.get('q')
    
    query = Product.query.filter_by(is_active=True)
    
    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    elif category:
        query = query.filter_by(category_id=category)
    
    if min_price is not None:
        query = query.filter(Product.discount_price.isnot(None), Product.discount_price >= min_price)
    if max_price is not None:
        query = query.filter(Product.discount_price.isnot(None), Product.discount_price <= max_price)
    
    if search:
        search_term = f"%{search}%"
        if lang == 'kn':
            query = query.filter(Product.name_kannada.ilike(search_term))
        else:
            query = query.filter(Product.name.ilike(search_term))
    
    if sort == 'price_low':
        query = query.order_by(Product.discount_price.asc().nullsfirst(), Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.discount_price.desc().nullslast(), Product.price.desc())
    elif sort == 'name':
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())
    
    products = query.all()
    
    if size:
        products = [p for p in products if size in p.get_sizes_list()]
    if color:
        products = [p for p in products if color in p.get_colors_list()]
    
    categories = Category.query.filter_by(is_active=True).all()
    
    all_sizes = set()
    all_colors = set()
    for p in Product.query.filter_by(is_active=True).all():
        all_sizes.update(p.get_sizes_list())
        all_colors.update(p.get_colors_list())
    
    return render_template('shop.html', 
                         products=products,
                         categories=categories,
                         all_sizes=sorted(all_sizes),
                         all_colors=sorted(all_colors),
                         category_slug=category_slug,
                         lang=lang)

@app.route('/search')
def search():
    """Instant search functionality"""
    lang = session.get('language', 'en')
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify({'products': [], 'message': ''})
    
    search_term = f"%{query}%"
    
    if lang == 'kn':
        products = Product.query.filter(Product.is_active == True, Product.name_kannada.ilike(search_term)).limit(10).all()
    else:
        products = Product.query.filter(Product.is_active == True, Product.name.ilike(search_term)).limit(10).all()
    
    if not products:
        return jsonify({'products': [], 'message': 'Item not available currently. It will be available within 2 days.'})
    
    results = []
    for p in products:
        results.append({
            'id': p.id,
            'name': p.name_kannada if lang == 'kn' else p.name,
            'price': p.get_final_price(),
            'image': p.image1,
            'url': url_for('product_detail', product_id=p.id)
        })
    
    return jsonify({'products': results, 'message': ''})

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    lang = session.get('language', 'en')
    product = Product.query.get_or_404(product_id)
    
    if current_user.is_authenticated:
        existing = RecentlyViewed.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if existing:
            existing.viewed_at = datetime.utcnow()
        else:
            viewed = RecentlyViewed(user_id=current_user.id, product_id=product_id)
            db.session.add(viewed)
        db.session.commit()
    
    related_products = Product.query.filter(Product.category_id == product.category_id, Product.id != product.id, Product.is_active == True).limit(4).all()
    
    in_wishlist = False
    if current_user.is_authenticated:
        in_wishlist = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first() is not None
    
    return render_template('product.html', product=product, related_products=related_products, in_wishlist=in_wishlist, lang=lang)

# ============ CART ROUTES ============

@app.route('/cart')
def cart():
    """Cart page"""
    lang = session.get('language', 'en')
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    else:
        cart_items = []
    return render_template('cart.html', cart_items=cart_items, lang=lang)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    """Add item to cart"""
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    size = request.form.get('size')
    color = request.form.get('color')
    
    product = Product.query.get_or_404(product_id)
    
    existing_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id, size=size, color=color).first()
    
    if existing_item:
        existing_item.quantity += quantity
        flash(f'Updated {product.name} quantity in cart!', 'success')
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity, size=size, color=color)
        db.session.add(cart_item)
        flash(f'Added {product.name} to cart!', 'success')
    
    db.session.commit()
    return redirect(request.referrer or url_for('cart'))

@app.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    """Update cart item quantity"""
    quantity = request.form.get('quantity', 1, type=int)
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('cart'))
    
    if quantity > 0:
        cart_item.quantity = quantity
    else:
        db.session.delete(cart_item)
    
    db.session.commit()
    flash('Cart updated!', 'success')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    """Remove item from cart"""
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id == current_user.id:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart!', 'success')
    return redirect(url_for('cart'))

# ============ WISHLIST ROUTES ============

@app.route('/wishlist')
@login_required
def wishlist():
    """Wishlist page"""
    lang = session.get('language', 'en')
    wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    return render_template('wishlist.html', wishlist_items=wishlist_items, lang=lang)

@app.route('/add_to_wishlist/<int:product_id>')
@login_required
def add_to_wishlist(product_id):
    """Add item to wishlist"""
    product = Product.query.get_or_404(product_id)
    existing = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if existing:
        db.session.delete(existing)
        flash(f'Removed {product.name} from wishlist!', 'info')
    else:
        wishlist_item = WishlistItem(user_id=current_user.id, product_id=product_id)
        db.session.add(wishlist_item)
        flash(f'Added {product.name} to wishlist!', 'success')
    
    db.session.commit()
    return redirect(request.referrer or url_for('wishlist'))

@app.route('/remove_from_wishlist/<int:item_id>')
@login_required
def remove_from_wishlist(item_id):
    """Remove item from wishlist"""
    item = WishlistItem.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Item removed from wishlist!', 'success')
    return redirect(url_for('wishlist'))

# ============ CHECKOUT ROUTES ============

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page"""
    lang = session.get('language', 'en')
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('shop'))
    
    form = CheckoutForm()
    
    if request.method == 'GET':
        form.shipping_name.data = current_user.username
        form.shipping_phone.data = current_user.phone
        form.shipping_address.data = current_user.address
        form.shipping_city.data = current_user.city
        form.shipping_state.data = current_user.state
        form.shipping_pincode.data = current_user.pincode
    
    if form.validate_on_submit():
        total = sum(item.get_total_price() for item in cart_items)
        order_number = f"AV{datetime.now().strftime('%Y%m%d%H%M%S')}{current_user.id}"
        
        order = Order(
            user_id=current_user.id,
            order_number=order_number,
            total_amount=total,
            shipping_name=form.shipping_name.data,
            shipping_phone=form.shipping_phone.data,
            shipping_address=form.shipping_address.data,
            shipping_city=form.shipping_city.data,
            shipping_state=form.shipping_state.data,
            shipping_pincode=form.shipping_pincode.data,
            payment_method=form.payment_method.data,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()
        
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.get_final_price(),
                size=item.size,
                color=item.color
            )
            db.session.add(order_item)
            
            # Reduce stock
            if item.product.stock >= item.quantity:
                item.product.stock -= item.quantity
        
        # Clear cart
        for item in cart_items:
            db.session.delete(item)
        
        db.session.commit()
        flash(f'Order placed successfully! Order number: {order_number}', 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))
    
    return render_template('checkout.html', form=form, cart_items=cart_items, lang=lang)

@app.route('/order_confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    """Order confirmation page"""
    lang = session.get('language', 'en')
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    return render_template('order_confirm.html', order=order, lang=lang)

# ============ USER AUTH ROUTES ============

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    lang = session.get('language', 'en')
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    
    return render_template('login.html', form=form, lang=lang)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    lang = session.get('language', 'en')
    form = RegistrationForm()
    
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match!', 'danger')
            return render_template('signup.html', form=form, lang=lang)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered!', 'danger')
            return render_template('signup.html', form=form, lang=lang)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken!', 'danger')
            return render_template('signup.html', form=form, lang=lang)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form, lang=lang)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    lang = session.get('language', 'en')
    form = ProfileForm()
    
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.address.data = current_user.address
        form.city.data = current_user.city
        form.state.data = current_user.state
        form.pincode.data = current_user.pincode
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.city = form.city.data
        current_user.state = form.state.data
        current_user.pincode = form.pincode.data
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', form=form, lang=lang)

@app.route('/orders')
@login_required
def orders():
    """User order history"""
    lang = session.get('language', 'en')
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders, lang=lang)

@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    """Order detail page"""
    lang = session.get('language', 'en')
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('orders'))
    return render_template('order_detail.html', order=order, lang=lang)

# ============ CONTACT & COMMENTS ROUTES ============

@app.route('/contact')
def contact():
    """Contact page"""
    lang = session.get('language', 'en')
    return render_template('contact.html', lang=lang)

@app.route('/comments', methods=['GET', 'POST'])
@login_required
def comments():
    """Comments/suggestions page"""
    lang = session.get('language', 'en')
    form = CommentForm()
    
    user_comments = Comment.query.filter_by(user_id=current_user.id).order_by(Comment.created_at.desc()).all()
    
    if form.validate_on_submit():
        comment = Comment(
            user_id=current_user.id,
            comment_type=form.comment_type.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your message has been submitted!', 'success')
        return redirect(url_for('comments'))
    
    return render_template('comments.html', form=form, user_comments=user_comments, lang=lang)

# ============ ADMIN ROUTES ============

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    lang = session.get('language', 'en')
    
    total_users = User.query.filter_by(is_admin=False).count()
    total_orders = Order.query.count()
    total_products = Product.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(Order.status != 'cancelled').scalar() or 0
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    low_stock_products = Product.query.filter(Product.stock < 10, Product.is_active == True).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_orders=total_orders,
                         total_products=total_products,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders,
                         low_stock_products=low_stock_products,
                         lang=lang)

@app.route('/admin/products')
@admin_required
def admin_products():
    """Manage products"""
    lang = session.get('language', 'en')
    products = Product.query.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=products, categories=categories, lang=lang)

@app.route('/admin/add_product', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    """Add new product"""
    lang = session.get('language', 'en')
    form = ProductForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        sizes_json = json.dumps([s.strip() for s in form.sizes.data.split(',')]) if form.sizes.data else json.dumps([])
        colors_json = json.dumps([c.strip() for c in form.colors.data.split(',')]) if form.colors.data else json.dumps([])
        
        product = Product(
            name=form.name.data,
            name_kannada=form.name_kannada.data,
            description=form.description.data,
            description_kannada=form.description_kannada.data,
            price=form.price.data,
            discount_price=form.discount_price.data,
            category_id=form.category.data,
            sizes=sizes_json,
            colors=colors_json,
            stock=form.stock.data,
            is_featured=form.is_featured.data,
            is_active=form.is_active.data,
            image1='product_placeholder.jpg'
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/add_product.html', form=form, lang=lang)

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    """Edit product"""
    lang = session.get('language', 'en')
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if request.method == 'GET':
        form.name.data = product.name
        form.name_kannada.data = product.name_kannada
        form.description.data = product.description
        form.description_kannada.data = product.description_kannada
        form.price.data = product.price
        form.discount_price.data = product.discount_price
        form.category.data = product.category_id
        form.sizes.data = ','.join(product.get_sizes_list())
        form.colors.data = ','.join(product.get_colors_list())
        form.stock.data = product.stock
        form.is_featured.data = product.is_featured
        form.is_active.data = product.is_active
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.name_kannada = form.name_kannada.data
        product.description = form.description.data
        product.description_kannada = form.description_kannada.data
        product.price = form.price.data
        product.discount_price = form.discount_price.data
        product.category_id = form.category.data
        product.sizes = json.dumps([s.strip() for s in form.sizes.data.split(',')]) if form.sizes.data else json.dumps([])
        product.colors = json.dumps([c.strip() for c in form.colors.data.split(',')]) if form.colors.data else json.dumps([])
        product.stock = form.stock.data
        product.is_featured = form.is_featured.data
        product.is_active = form.is_active.data
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/edit_product.html', form=form, product=product, lang=lang)

@app.route('/admin/delete_product/<int:product_id>')
@admin_required
def admin_delete_product(product_id):
    """Delete product"""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    """Manage orders"""
    lang = session.get('language', 'en')
    status_filter = request.args.get('status')
    
    if status_filter:
        orders = Order.query.filter_by(status=status_filter).order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.order_by(Order.created_at.desc()).all()
    
    return render_template('admin/orders.html', orders=orders, lang=lang)

@app.route('/admin/update_order/<int:order_id>', methods=['POST'])
@admin_required
def admin_update_order(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get('status')
    db.session.commit()
    flash(f'Order {order.order_number} status updated!', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/offers')
@admin_required
def admin_offers():
    """Manage offers"""
    lang = session.get('language', 'en')
    offers = Offer.query.order_by(Offer.created_at.desc()).all()
    products = Product.query.filter_by(is_active=True).all()
    return render_template('admin/offers.html', offers=offers, products=products, lang=lang)

@app.route('/admin/add_offer', methods=['POST'])
@admin_required
def admin_add_offer():
    """Add new offer"""
    form = OfferForm()
    form.product.choices = [(0, 'All Products')] + [(p.id, p.name) for p in Product.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        product_id = form.product.data if form.product.data != 0 else None
        
        offer = Offer(
            title=form.title.data,
            title_kannada=form.title_kannada.data,
            description=form.description.data,
            description_kannada=form.description_kannada.data,
            discount_percentage=form.discount_percentage.data,
            product_id=product_id,
            is_active=form.is_active.data
        )
        db.session.add(offer)
        db.session.commit()
        flash('Offer added successfully!', 'success')
    
    return redirect(url_for('admin_offers'))

@app.route('/admin/delete_offer/<int:offer_id>')
@admin_required
def admin_delete_offer(offer_id):
    """Delete offer"""
    offer = Offer.query.get_or_404(offer_id)
    db.session.delete(offer)
    db.session.commit()
    flash('Offer deleted successfully!', 'success')
    return redirect(url_for('admin_offers'))

@app.route('/admin/comments')
@admin_required
def admin_comments():
    """Manage customer comments"""
    lang = session.get('language', 'en')
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return render_template('admin/comments.html', comments=comments, lang=lang)

@app.route('/admin/respond_comment/<int:comment_id>', methods=['POST'])
@admin_required
def admin_respond_comment(comment_id):
    """Respond to comment"""
    comment = Comment.query.get_or_404(comment_id)
    comment.admin_response = request.form.get('response')
    comment.is_answered = True
    comment.responded_by = current_user.id
    comment.responded_at = datetime.utcnow()
    db.session.commit()
    flash('Response submitted!', 'success')
    return redirect(url_for('admin_comments'))

@app.route('/admin/users')
@admin_required
def admin_users():
    """Manage users"""
    lang = session.get('language', 'en')
    users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users, lang=lang)

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error_code=500, error_message='Internal server error'), 500

# ============ MAIN ============

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Run the app
    # Run without the reloader when debugging issues with request handling
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=8000)

