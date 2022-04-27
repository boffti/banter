import json
import os
import arrow
from random import sample
from functools import wraps
import cloudinary
import cloudinary.uploader as _cu
from dotenv import load_dotenv
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   send_file, session, url_for)
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import datetime
import math

from models import (Admin, BillboardPost, Club, ClubPost, Event, ProductCategory, School,
                    Student, UserRoles, ClubMembers, Product, Order, Advertisement, BroadcastMessage, 
                    PaymentMethod, BillboardCategories, db_init)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
db = db_init(app)

INIT_DP = "https://res.cloudinary.com/dtvhyzofv/image/upload/v1647144583/banter/dp/user_awjxuf.png"
CLUB_IMG_PATH = 'banter/clubs/'
PRODUCT_IMG_PATH = 'banter/product/'
AD_IMG_PATH = 'banter/advertisement/'
DP_IMG_PATH = 'banter/dp/'
ALLOWED_TYPES = ['image/jpeg', 'image/png']

cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('CLOUD_API_KEY'),
    api_secret=os.getenv('CLOUD_API_SECRET')
)

# UTIL Functions --------------------------------------------------------------
def get_ads():
    ads = Advertisement.query.filter_by(school_id=session['user']['school_id']).all()
    ads = [a.format() for a in ads]
    return ads

# Inject Ads Algorithm
def inject_ads(data):
    if len(data) == 0:
        return data
    ads = get_ads()
    idx = math.ceil(len(data)/(len(ads)+1))
    # idx = (len(data)//(len(ads)+1))
    k, m = 1, 0
    for ad in ads:
        data.insert(idx * k + m, ad)
        k, m = k+1, m+1
    return data

def get_notifications():
    notifications = BroadcastMessage.query.filter_by(school_id=session['user']['school_id']).all()
    notifications = [n.format() for n in notifications]
    session['broadcast_messages'] = notifications

def get_clubs(n=6, no_ad=False):
    if no_ad:
        return  Club.query.filter_by(school_id=session['user']['school_id']).all()
    else:
        if n == 'all':
            clubs = Club.query.filter_by(school_id=session['user']['school_id']).all()
        else:
            clubs = Club.query.filter_by(school_id=session['user']['school_id']).limit(n).all()
        clubs = [p.format() for p in clubs]
        return inject_ads(clubs)

def get_billboard_posts(n=6):
    if n == 'all':
        posts = BillboardPost.query.filter_by(school_id=session['user']['school_id']).all()
    else:
        posts = BillboardPost.query.filter_by(school_id=session['user']['school_id']).limit(n).all()
    posts = [p.format() for p in posts]
    return inject_ads(posts)

def get_events():
    events = Event.query.filter_by(
        school_id=session['user']['school_id']).all()
    events = [e.format() for e in events]
    for e in events:
        e["date"] = e.get('date_time').strftime("%b %d")
        e["time"] = e.get('date_time').strftime("%I:%M %p")
    return events

def pop_search():
    if 'search_term' in session:
        session.pop('search_term')
    if 'num_products' in session:
        session.pop('num_products')
    if 'num_clubs' in session:
        session.pop('num_clubs')
    if 'num_events' in session:
        session.pop('num_events')
    if 'num_users' in session:
        session.pop('num_users')
    if 'num_posts' in session:
        session.pop('num_posts')

@app.template_filter('is_member')
def is_member(value):
    if ClubMembers.query.filter_by(student_id=session['user']['id'], club_id=value).first():
        return True
    return False

@app.template_filter('card_type')
def card_type(value):
    number = str(value)
    cardtype = ""
    if len(number) == 15:
        if number[:2] == "34" or number[:2] == "37":
            cardtype = "americanexpress"
    if len(number) == 13:
        if number[:1] == "4":
            cardtype = "visa"
    if len(number) == 16:
        if number[:4] == "6011":
            cardtype = "discover"
        if int(number[:2]) >= 51 and int(number[:2]) <= 55:
            cardtype = "mastercard"
        if number[:1] == "4":
            cardtype = "visa"
        if number[:4] == "3528" or number[:4] == "3529":
            cardtype = "jcb"
        if int(number[:3]) >= 353 and int(number[:3]) <= 359:
            cardtype = "jcb"
    if len(number) == 14:
        if number[:2] == "36":
            cardtype = "dinersclub"
        if int(number[:3]) >= 300 and int(number[:3]) <= 305:
            cardtype = "dinersclub"
    return cardtype

@app.template_filter('humanize')
def humanize(value):
    return arrow.Arrow.fromdatetime(value).humanize()

@app.template_filter('get_product')
def get_product(value):
    return Product.query.filter_by(id=value).first()

@app.template_filter('get_total')
def get_total(value):
    total = 0
    for id in session['cart']:
        product = get_product(id)
        total += product.price
    return total

@app.template_filter('get_sale_count')
def get_sale_count(value):
    order = Order.query.filter_by(seller_id=value.get('id')).all()
    return len(order)

@app.template_filter('no_purchases')
def no_purchase(value):
    for product in value:
        if product.purchased:
            return False
    return True

@app.template_filter('precision_2')
def precision_2(value):
    return "{:.2f}".format(value)

@app.template_filter('get_sold_count')
def get_sold_count(value):
    count = 0
    for product in value:
        if product.purchased:
            count += 1
    return count == len(value)
# -----------------------------------------------------------------------------

# Admin Auth Decorator
def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        roles = session.get('user_roles')
        if len(roles) == 0:
            flash('Not Authorized')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Home Route --------------------------------------------------------------------
@app.route('/')
def home():
    if 'user' not in session:
        return render_template('login/login.html')
    else:
        get_notifications()
        if 'cart' not in session:
            session['cart'] = []
        clubs = get_clubs(no_ad=True)
        sample_size = min(len(clubs), 6)
        clubs = sample(clubs, sample_size) if len(clubs) > 0 else []
        events = get_events()
        sample_size = min(len(events), 6)
        events = sample(events, sample_size) if len(events) > 0 else []
        return render_template('index.html', billboard=get_billboard_posts(), events=events, clubs=clubs)
# -----------------------------------------------------------------------------

# Login & Register Routes --------------------------------------------------------------
# Register Route GET
@app.route('/register')
def register():
    if 'user' not in session:
        schools = [school.format() for school in School.query.all()]
        return render_template('login/register.html', schools=schools)
    else:
        return redirect(url_for('home'))

# Register Route POST
@app.route('/register', methods=['POST'])
def register_user():
    if 'user' not in session:
        name = request.form['name']
        school_id = request.form['id']
        school = request.form['school']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('register'))
        else:
            try:
                school = School.query.filter_by(id=school).first()
                if school is None:
                    flash('Invalid School ID!')
                    return redirect(url_for('register'))
                else:
                    new_user = Student(id=school_id, name=name, password=sha256.hash(
                        password), bio='Awesome Student', dob='', school_id=school.id, dp=INIT_DP, major='', phone='')
                    new_user.insert()
                    session['user'] = new_user.format()
                    flash("Welcome to your best campus life, {}!".format(
                        session['user']['name']))
                    return redirect(url_for('home'))
            except Exception as e:
                print(f'Error ==> {e}')
                flash('Something went wrong!')
                return redirect(url_for('register'))
    else:
        return redirect(url_for('home'))

# Login Route GET
@app.route('/login')
def login_page():
    if 'user' not in session:
        return render_template('login/login.html')
    else:
        return redirect(url_for('home'))

# Login Route POST
@app.route('/login', methods=['POST'])
def login_user():
    login_creds = request.form.to_dict()
    if login_creds['id'] == '' or login_creds['pass'] == '':
        flash('Please enter a username and password')
        return redirect(url_for('login_page'))
    else:
        user = Student.query.filter_by(id=login_creds['id']).first()
        if user and sha256.verify(login_creds['pass'], user.password):
            user_roles = UserRoles.query.filter_by(student_id=user.id).all()
            roles = [role.role_id for role in user_roles]
            session['user_roles'] = roles
            print(f'User Roles ==> {roles}')
            session['user'] = user.format()
            flash('Welcome back, {}!'.format(session['user']['name']))
            return redirect(url_for('home'))
        else:
            flash('Incorrect username or password')
            return redirect(url_for('login_page'))

# Logout Route
@app.route('/logout')
def logout():
    # Remove the user from session
    if 'user' in session:
        session.pop('user')
        if 'user_roles' in session:
            session.pop('user_roles')
    if 'broadcast_messages' in session:
        session.pop('broadcast_messages')
    return redirect(url_for('login_page'))
# -----------------------------------------------------------------------------------

# Profile Routes ---------------------------------------------------------------
@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    else:
        student = Student.query.filter_by(id=session['user']['id']).first()
        billboard_posts = BillboardPost.query.filter_by(
            student_id=session['user']['id']).all()
        billboard_posts = [post.format() for post in billboard_posts]
        club_posts = ClubPost.query.filter_by(
            student_id=session['user']['id']).all()
        club_posts = [post.format() for post in club_posts]
        events = Event.query.filter_by(student_id=session['user']['id']).all()
        events = [e.format() for e in events]
        owned_clubs = Club.query.filter_by(
            owner_id=session['user']['id']).all()
        owned_clubs = [club.format() for club in owned_clubs]
        for e in events:
            e["date"] = e.get('date_time').strftime("%b %d")
            e["time"] = e.get('date_time').strftime("%I:%M %p")
        return render_template('user/profile.html', student=student, billboard_posts=billboard_posts, club_posts=club_posts, events=events, owned_clubs=owned_clubs)

@app.route('/student/<id>')
def other_profile(id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    student = Student.query.filter_by(id=id).first()
    billboard_posts = BillboardPost.query.filter_by(student_id=id).all()
    billboard_posts = [post.format() for post in billboard_posts]
    club_posts = ClubPost.query.filter_by(student_id=id).all()
    club_posts = [post.format() for post in club_posts]
    events = Event.query.filter_by(student_id=id).all()
    events = [e.format() for e in events]
    owned_clubs = Club.query.filter_by(owner_id=id).all()
    owned_clubs = [club.format() for club in owned_clubs]
    for e in events:
        e["date"] = e.get('date_time').strftime("%b %d")
        e["time"] = e.get('date_time').strftime("%I:%M %p")
    return render_template('user/other_user_profile.html', student=student, billboard_posts=billboard_posts, club_posts=club_posts, events=events, owned_clubs=owned_clubs)

@app.route('/update-dp', methods=['POST'])
def update_dp():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    dp = request.files['file']
    if dp.filename != '':
        try:
            # Uploading to cloudinary
            if dp.content_type not in ALLOWED_TYPES:
                flash("Invalid image type. Please upload a jpeg or png image.")
                return redirect(request.url)
            res = _cu.upload(dp, folder=DP_IMG_PATH)
            user_id = session['user']['id']
            user = Student.query.filter_by(id=user_id).first()
            user.dp = res['secure_url']
            user.update()
            session['user'] = user.format()
            return '1'
        except Exception as e:
            print(f'Error ==> {e}')
    else:
        return '0'

@app.route('/update-profile', methods=['POST'])
def update_profile():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    data = request.form.to_dict()
    user_id = session['user']['id']
    user = Student.query.filter_by(id=user_id).first()
    user.name = data['name']
    user.bio = data['bio']
    user.phone = data['phone']
    user.dob = data['dob']
    user.major = data['major']
    user.update()
    session['user'] = user.format()
    flash('Profile updated successfully!')
    return redirect(request.referrer)
# ------------------------------------------------------------------------------

# BillBoard Routes ------------------------------------------------------------
@app.route('/billboard')
def billboard_page():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    if 'billboard_category' in session:
        session.pop('billboard_category')
    billboard_posts = get_billboard_posts('all')
    categories = BillboardCategories.query.all()
    return render_template('billboard/billboard.html', billboard=billboard_posts, categories=categories)

@app.route('/billboard/post', methods=['POST'])
def add_billboard_post():
    # TODO - Create a billboard post
    return redirect(request.referrer)


@app.route('/billboard/post/delete/<post_id>', methods=['DELETE'])
def delete_billboard_post(post_id):
    # TODO - Delete billboard post
    return redirect(request.referrer)

@app.route('/billboard/category/<int:category_id>')
def get_billboard_by_category(category_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    if category_id == 0:
        return redirect(url_for('billboard_page'))
    session['billboard_category'] = BillboardCategories.query.filter_by(id=category_id).first().name
    billboard_posts = BillboardPost.query.filter_by(
    school_id=session['user']['school_id']).filter_by(tag_id=category_id).order_by(BillboardPost.created_at.desc()).all()
    categories = BillboardCategories.query.all()
    return render_template('billboard/billboard.html', billboard=billboard_posts, categories=categories)
# ------------------------------------------------------------------------------

# Club Routes ----------------------------------------------------------------------
@app.route('/clubs')
def club():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    return render_template('club/clubs.html', clubs=get_clubs('all'))

@app.route('/clubs/<club_id>')
def club_details(club_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    else:
        club = Club.query.filter_by(id=club_id).first()
        club_posts = ClubPost.query.filter_by(club_id=club_id).all()
        club_posts = [post.format() for post in club_posts]
        return render_template('club/club_detail.html', club=club, club_posts=club_posts)

@app.route('/create-club', methods=['POST'])
def create_club():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    data = request.form.to_dict()
    file = request.files['file']
    if data['name'] == '' or data['description'] == '':
        flash('Please fill in all the fields.')
        return redirect(request.referrer)
    if file.filename == '':
        flash('Please select an image to upload.')
        return redirect(request.referrer)
    try:
        # Uploading to cloudinary
        if file.content_type not in ALLOWED_TYPES:
            flash("Invalid image type. Please upload a jpeg or png image.")
            return redirect(request.url)
        res = _cu.upload(file, folder=CLUB_IMG_PATH)
        club = Club(name=data['name'], description=data['description'], school_id=session['user']
                    ['school_id'], img_url=res['secure_url'], owner_id=session['user']['id'])
        club.insert()
        flash('Club created successfully!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(url_for('home'))

@app.route('/club-post/<club_id>', methods=['POST'])
def add_club_post(club_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        data = request.form.to_dict()
        if data['content'] == '':
            flash('Please enter a message to post.')
            return redirect(request.referrer)
        club_post = ClubPost(title=data['title'], content=data['content'],
                             club_id=club_id, student_id=session['user']['id'])
        club_post.insert()
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/join-club/<club_id>')
def join_club(club_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    club_member = ClubMembers(
        club_id=club_id, student_id=session['user']['id'])
    club_member.insert()
    flash('You have joined the club!')
    return redirect(request.referrer)

@app.route('/exit-club/<club_id>')
def exit_club(club_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    club_member = ClubMembers.query.filter_by(
        club_id=club_id, student_id=session['user']['id']).first()
    club_member.delete()
    flash('You have successfully exited the club!')
    return redirect(request.referrer)

@app.route('/delete-club-post/<post_id>')
def delete_club_post(post_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        club_post = ClubPost.query.filter_by(id=post_id).first()
        club_post.delete()
        flash('Post deleted successfully!')
        return redirect(request.referrer)
    except Exception as e:
        print(f'Error ==> {e}')
        flash('Something went wrong')
        return redirect(request.referrer)

@app.route('/delete-club/<club_id>')
def delete_club(club_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        club = Club.query.filter_by(id=club_id).first()
        club_posts = ClubPost.query.filter_by(club_id=club_id).all()
        for post in club_posts:
            post.delete()
        club_members = ClubMembers.query.filter_by(club_id=club_id).all()
        for member in club_members:
            member.delete()
        club.delete()
        flash('Club deleted successfully')
        return redirect(request.referrer)
    except Exception as e:
        print(f'Error ==> {e}')
        flash('Something went wrong')
        return redirect(request.referrer)

# Search Clubs
@app.route('/clubs/search', methods=['GET','POST'])
def clubs_search():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        search_term = request.form.get('searchTerm', '')
        clubs = Club.query.filter_by(school_id=session['user']['school_id']).filter(Club.name.ilike(f'%{search_term}%')).all()
        return render_template('club/clubs.html', clubs=clubs)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)
# ----------------------------------------------------------------------------

# Shop Routes ---------------------------------------------------------------
@app.route('/shop')
def get_shop_page():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    if 'shop_category' in session:
        session.pop('shop_category')
    products = Product.query.filter_by(
        school_id=session['user']['school_id']).filter_by(purchased=False).order_by(Product.created_at.desc()).all()
    categories = ProductCategory.query.all()
    return render_template('shop/shop.html', products=inject_ads(products), categories=categories)

@app.route('/cart')
def cart_page():
    if len(session.get('cart')) == 0:
        flash('Your cart is empty!')
        return redirect(url_for('get_shop_page'))
    student = Student.query.filter_by(id=session['user']['id']).first()
    return render_template('/shop/cart.html', student=student)

@app.route('/add-to-cart/<product_id>')
def add_to_cart(product_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        product = Product.query.filter_by(id=product_id).first()
        if product.seller_id == session['user']['id']:
            flash('You cannot buy your own product!')
            return redirect(request.referrer)
        if 'cart' not in session:
            session['cart'] = []
        session['cart'].append(product.id)
        flash('Product added to cart!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/delete-from-cart/<int:product_id>')
def delete_from_cart(product_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        if 'cart' not in session:
            session['cart'] = []
        session['cart'].remove(product_id)
        flash('Product removed from cart!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/add-product', methods=['POST'])
def add_product():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        data = request.form.to_dict()
        file = request.files['file']
        if data['name'] == '' or data['description'] == '' or data['price'] == '':
            flash('Please fill in all the fields.')
            return redirect(request.referrer)
        if file.filename == '':
            flash('Please select an image to upload.')
            return redirect(request.referrer)
        if file.content_type not in ALLOWED_TYPES:
            flash("Invalid image type. Please upload a jpeg or png image.")
            return redirect(request.referrer)
        res = _cu.upload(file, folder=PRODUCT_IMG_PATH)
        product = Product(name=data['name'], price=data['price'], description=data['description'], img_url=res['secure_url'], category_id=data['category'],
                          school_id=session['user']['school_id'], created_at=datetime.now(), seller_id=session['user']['id'], purchased=False)
        product.insert()
        flash('Product created successfully!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/add-payment', methods=['POST'])
def add_payment():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        data = request.form.to_dict()
        if data['card_number'] == '' or data['name_on_card'] == '' or data['cvv'] == '' or data['zip_code'] == '':
            flash('Please fill in all the fields.')
            return redirect(request.referrer)
        date_str = f'{data["exp_month"]}/01/{data["exp_year"]}'
        expiry_date = datetime.strptime(date_str, '%m/%d/%Y')
        payment = PaymentMethod(student_id=session['user']['id'], card_number=data['card_number'].replace(" ", ""), name_on_card=data['name_on_card'], cvv=data['cvv'], zip_code=data['zip_code'], valid_through=expiry_date)
        payment.insert()
        flash('Payment created successfully!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/delete-payment/<int:payment_id>')
def delete_paymenr(payment_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        payment = PaymentMethod.query.filter_by(id=payment_id).first()
        if payment.student_id != session['user']['id']:
            flash('You cannot delete this payment!')
            return redirect(request.referrer)
        payment.delete()
        flash('Payment deleted successfully!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/checkout')
def checkout():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    if 'cart' not in session or len(session['cart']) == 0:
        flash('Your cart is empty!')
        return redirect(request.referrer)
    try:
        for id in session['cart']:
            product = Product.query.filter_by(id=id).first()
            if Order.query.filter_by(product_id=id).first():
                session['cart'].remove(id)
                flash(
                    f'{product.name} has already been purchased! Product removed from cart. Place order again.')
                return redirect(request.referrer)
            product.purchased = True
            product.update()
            order = Order(
                product_id=id, buyer_id=session['user']['id'], seller_id=product.seller.id, created_at=datetime.now())
            order.insert()
            session['cart'] = []
        flash('Order placed successfully!')
        return redirect(url_for('get_shop_page'))
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/my-products')
def my_products():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    categories = ProductCategory.query.all()
    products = Product.query.filter_by(seller_id=session['user']['id']).all()
    for product in products:
        if product.purchased:
            order = Order.query.filter_by(product_id=product.id).first()
            product.buyer = order.buyer
            product.buyer.created_at = order.created_at
            product.order_id = order.id
        else:
            product.buyer = None
    return render_template('user/products.html', products=products, categories=categories)

@app.route('/my-purchases')
def my_purchases():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    orders = Order.query.filter_by(buyer_id=session['user']['id']).all()
    return render_template('user/purchases.html', orders=orders)


@app.route('/cancel-order/<int:order_id>')
def cancel_order(order_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        order = Order.query.filter_by(id=order_id).first()
        product = Product.query.filter_by(id=order.product_id).first()
        product.purchased = False
        product.update()
        order.delete()
        flash('Order cancelled successfully!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/shop/search', methods=['GET','POST'])
def shop_search():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        if 'shop_category' in session:
            session.pop('shop_category')
        search_term = request.form.get('searchTerm', '')
        products = Product.query.filter_by(
            school_id=session['user']['school_id']).filter_by(purchased=False).filter(Product.name.ilike(f'%{search_term}%')).order_by(Product.created_at.desc()).all()
        categories = ProductCategory.query.all()
        return render_template('shop/shop.html', products=products, categories=categories)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/shop/category/<int:category_id>')
def get_shop_by_category(category_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    if category_id == 0:
        return redirect(url_for('get_shop_page'))
    session['shop_category'] = ProductCategory.query.filter_by(id=category_id).first().name
    products = Product.query.filter_by(
    school_id=session['user']['school_id']).filter_by(purchased=False).filter_by(category_id=category_id).order_by(Product.created_at.desc()).all()
    categories = ProductCategory.query.all()
    return render_template('shop/shop.html', products=products, categories=categories)

@app.route('/shop/delete-product/<int:product_id>')
def delete_product(product_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        product = Product.query.filter_by(id=product_id).first()
        if product.seller_id != session['user']['id']:
            flash('You are not authorized to delete this product!')
            return redirect(request.referrer)
        product.delete()
        flash('Product deleted successfully!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)
# ----------------------------------------------------------------------------

# Event routes ---------------------------------------------------------------
@app.route('/events')
def events():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    events = get_events()
    return render_template('events/events.html', events=inject_ads(events))

@app.route('/events', methods=['POST'])
def insertEvent():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    data = request.form.to_dict()
    if data['name'] == '' or data['description'] == '' or data['time'] == '':
        flash('Please fill in all the fields.')
        return redirect(request.referrer)
    try:
        # Example - 2022-03-17 05:30 pm
        date_time = datetime.strptime(
            data['date'] + ' ' + data['time'] + ' ' + data['ampm'], '%Y-%m-%d %I:%M %p')
        event = Event(name=data['name'], description=data['description'], date_time=date_time,
                      location=data['location'], student_id=session['user']['id'], school_id=session['user']['school_id'])
        event.insert()
        flash('Event created successfully!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/delete-event/<event_id>')
def delete_event(event_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        event = Event.query.filter_by(id=event_id).first()
        event.delete()
        flash('Event deleted successfully!')
        return redirect(request.referrer)
    except:
        flash("Something went wrong!")
        return redirect(request.referrer)

# Search Events
@app.route('/events/search', methods=['GET','POST'])
def events_search():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        search_term = request.form.get('searchTerm', '')
        events = Event.query.filter_by(school_id=session['user']['school_id']).filter(Event.name.ilike(f'%{search_term}%')).all()
        events = [e.format() for e in events]
        for e in events:
            e["date"] = e.get('date_time').strftime("%b %d")
            e["time"] = e.get('date_time').strftime("%I:%M %p")
        return render_template('events/events.html', events=events)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)
# ----------------------------------------------------------------------------

@app.route('/about')
def about_page():
    return render_template('other/about.html')

@app.route('/faq')
def faq_page():
    return render_template('other/faq.html')

# Admin Routes ---------------------------------------------------------------
@app.route('/admin')
@requires_auth
def admin_page():
    schools = School.query.all()
    user_roles = UserRoles.query.filter_by(role_id=2).all()
    return render_template('admin/admin.html', schools=schools, school_admins=user_roles)

@app.route('/school_admin')
@requires_auth
def school_admin():
    students = Student.query.filter_by(
        school_id=session['user']['school_id']).all()
    posts = BillboardPost.query.filter_by(
        school_id=session['user']['school_id']).all()
    events = Event.query.filter_by(school_id=session['user']['school_id']).all()
    ads = Advertisement.query.filter_by(
        school_id=session['user']['school_id']).all()
    broadcast_messages = BroadcastMessage.query.filter_by(
        school_id=session['user']['school_id']).all()
    return render_template('admin/school_admin.html', students=students, posts=posts, events=events, ads=ads, broadcast_messages=broadcast_messages)

@app.route('/create-ad', methods=['POST'])
def create_ad():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        data = request.form.to_dict()
        file = request.files['file']
        if data['title'] == '' or data['description'] == '' or data['ext_link'] == '':
            flash('Please fill in all the fields.')
            return redirect(request.referrer)
        if file.filename == '':
            flash('Please select an image to upload.')
            return redirect(request.referrer)
        if file.content_type not in ALLOWED_TYPES:
            flash("Invalid image type. Please upload a jpeg or png image.")
            return redirect(request.referrer)
        res = _cu.upload(file, folder=AD_IMG_PATH)
        ad = Advertisement(title=data['title'], description=data['description'], ext_link=data['ext_link'], img_url=res['secure_url'], school_id=session['user']['school_id'], admin_id=session['user']['id'])
        ad.insert()
        flash('Ad created successfully!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/delete-ad/<int:ad_id>')
def delete_ad(ad_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        ad = Advertisement.query.filter_by(id=ad_id).first()
        if ad.admin_id != session['user']['id']:
            flash('You are not authorized to delete this ad!')
            return redirect(request.referrer)
        ad.delete()
        flash('Ad deleted successfully!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/create-broadcast', methods=['POST'])
def create_broadcast():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        data = request.form.to_dict()
        if data['title'] == '' or data['content'] == '':
            flash('Please fill in all the fields.')
            return redirect(request.referrer)
        message = BroadcastMessage(title=data['title'], content=data['content'], school_id=session['user']['school_id'], created_at = datetime.now())
        message.insert()
        get_notifications()
        flash('Broadcast created successfully!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/delete-broadcast/<int:broadcast_id>')
def delete_broadcast(broadcast_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    try:
        broadcast = BroadcastMessage.query.filter_by(id=broadcast_id).first()
        if broadcast.school_id != session['user']['school_id']:
            flash('You are not authorized to delete this broadcast!')
            return redirect(request.referrer)
        broadcast.delete()
        get_notifications()
        flash('Broadcast deleted successfully!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)
# ----------------------------------------------------------------------------

# Search Routes --------------------------------------------------------------
@app.route('/search', methods=['GET','POST'])
def search_page():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    if request.method == 'GET':
        if 'search_term' not in session:
            return redirect(url_for('home'))
    try:
        # pop_search()
        if request.method == 'POST':
            search_term = request.form.get('search_term')
            if search_term == '':
                flash('Please enter a search term.')
                return redirect(request.referrer)
            session['search_term'] = search_term

        products_1 = Product.query.filter_by(school_id=session['user']['school_id']).filter(Product.name.ilike('%' + session.get('search_term') + '%' )).all()
        products_2 = Product.query.filter_by(school_id=session['user']['school_id']).filter(Product.description.ilike('%' + session.get('search_term') + '%' )).all()
        products = set(products_1 + products_2)
        session['num_products'] = len(products)

        events_1 = Event.query.filter_by(school_id=session['user']['school_id']).filter(Event.name.ilike('%' + session.get('search_term') + '%' )).all()
        events_2 = Event.query.filter_by(school_id=session['user']['school_id']).filter(Event.description.ilike('%' + session.get('search_term') + '%' )).all()
        events = set(events_1 + events_2)
        session['num_events'] = len(events)

        posts_1 = BillboardPost.query.filter_by(school_id=session['user']['school_id']).filter(BillboardPost.title.ilike('%' + session.get('search_term') + '%' )).all()
        posts_2 = BillboardPost.query.filter_by(school_id=session['user']['school_id']).filter(BillboardPost.content.ilike('%' + session.get('search_term') + '%' )).all()
        posts = set(posts_1 + posts_2)
        session['num_posts'] = len(posts)

        clubs_1 = Club.query.filter_by(school_id=session['user']['school_id']).filter(Club.name.ilike('%' + session.get('search_term') + '%' )).all()
        clubs_2 = Club.query.filter_by(school_id=session['user']['school_id']).filter(Club.description.ilike('%' + session.get('search_term') + '%' )).all()
        clubs = set(clubs_1 + clubs_2)
        session['num_clubs'] = len(clubs)

        students_1 = Student.query.filter_by(school_id=session['user']['school_id']).filter(Student.name.ilike('%' + session.get('search_term') + '%' )).all()
        students_2 = Student.query.filter_by(school_id=session['user']['school_id']).filter(Student.id.ilike('%' + session.get('search_term') + '%' )).all()
        students = set(students_1 + students_2)
        session['num_students'] = len(students)

        session['total_results'] = len(products) + len(events) + len(posts) + len(clubs) + len(students)

        if len(products) == 0:
                return redirect(url_for('search_page_event'))

        return render_template('search/product_results.html', products=products)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(request.referrer)

@app.route('/search/billboard')
def search_page_billboard():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    posts_1 = BillboardPost.query.filter_by(school_id=session['user']['school_id']).filter(BillboardPost.title.ilike('%' + session.get('search_term') + '%' )).all()
    posts_2 = BillboardPost.query.filter_by(school_id=session['user']['school_id']).filter(BillboardPost.content.ilike('%' + session.get('search_term') + '%' )).all()
    posts = list(set(posts_1 + posts_2))
    posts = [p.format() for p in posts]
    session['num_posts'] = len(posts)
    if len(posts) == 0:
        return redirect(url_for('search_page_club'))
    return render_template('search/billboard_results.html', posts=posts)

@app.route('/search/clubs')
def search_page_club():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    clubs_1 = Club.query.filter_by(school_id=session['user']['school_id']).filter(Club.name.ilike('%' + session.get('search_term') + '%' )).all()
    clubs_2 = Club.query.filter_by(school_id=session['user']['school_id']).filter(Club.description.ilike('%' + session.get('search_term') + '%' )).all()
    clubs = set(clubs_1 + clubs_2)
    session['num_clubs'] = len(clubs)
    if len(clubs) == 0:
        return redirect(url_for('search_page_users'))
    return render_template('search/clubs_results.html', clubs=clubs)

@app.route('/search/events')
def search_page_event():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    events_1 = Event.query.filter_by(school_id=session['user']['school_id']).filter(Event.name.ilike('%' + session.get('search_term') + '%' )).all()
    events_2 = Event.query.filter_by(school_id=session['user']['school_id']).filter(Event.description.ilike('%' + session.get('search_term') + '%' )).all()
    events = list(set(events_1 + events_2))
    events = [e.format() for e in events]
    for e in events:
        e["date"] = e.get('date_time').strftime("%b %d")
        e["time"] = e.get('date_time').strftime("%I:%M %p")
    session['num_events'] = len(events)
    if len(events) == 0:
        return redirect(url_for('search_page_billboard'))
    return render_template('search/events_results.html', events=events)

@app.route('/search/products')
def search_page_product():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    products_1 = Product.query.filter(Product.name.ilike('%' + session.get('search_term') + '%' )).all()
    products_2 = Product.query.filter(Product.description.ilike('%' + session.get('search_term') + '%' )).all()
    products = set(products_1 + products_2)
    session['num_products'] = len(products)
    if len(products) == 0:
        return redirect(url_for('search_page_event'))
    return render_template('search/product_results.html', products=products)

@app.route('/search/users')
def search_page_users():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    students_1 = Student.query.filter_by(school_id=session['user']['school_id']).filter(Student.name.ilike('%' + session.get('search_term') + '%' )).all()
    students_2 = Student.query.filter_by(school_id=session['user']['school_id']).filter(Student.id.ilike('%' + session.get('search_term') + '%' )).all()
    students = set(students_1 + students_2)
    session['num_students'] = len(students)
    return render_template('search/users_results.html', students=students)
# ----------------------------------------------------------------------------

# Schools dropdown route
@app.route('/schools')
def getSchools():
    schools = School.query.all()
    schoolsResponse = [school.format() for school in schools]
    return json.dumps(schoolsResponse)

@app.route('/test')
def test():
    students = Student.query.all()
    studentResponse = [student.format() for student in students]
    return json.dumps(studentResponse)

@app.route('/session')
def get_session():
    return jsonify(session)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
