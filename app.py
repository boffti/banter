from multiprocessing import Event
from unicodedata import name
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                    session, url_for, send_file)
import json
from models import Student, School, Admin, Club, BillboardPost, ClubPost, Event, db_init
from random import sample
from passlib.hash import pbkdf2_sha256 as sha256
from mock_data import events
import cloudinary
import cloudinary.uploader as _cu
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
db = db_init(app)

CLUB_IMG_PATH = 'banter/clubs/'
DP_IMG_PATH = 'banter/dp/'
ALLOWED_TYPES = ['image/jpeg', 'image/png']

cloudinary.config(
    cloud_name = os.getenv('CLOUD_NAME'),
    api_key = os.getenv('CLOUD_API_KEY'),
    api_secret = os.getenv('CLOUD_API_SECRET')
)

def get_clubs():
    clubs = Club.query.filter_by(school_id=session['user']['school_id']).all()
    return clubs

def get_billboard_posts():
    posts = BillboardPost.query.filter_by(school_id=session['user']['school_id']).all()
    return posts

@app.route('/')
def home():
    if 'user' not in session:
        return render_template('login/login.html')
    else:
        return render_template('index.html', billboard=get_billboard_posts(), events=events, clubs=sample(get_clubs(), 6))

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
        school = "UTA"
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
                    new_user = Student(id=school_id, name=name, password=sha256.hash(password), bio='Awesome Student', dob='Made in China', school_id=school.id, dp='user.png')
                    new_user.insert()
                    session['user'] = new_user.format()
                    return redirect(url_for('login_page'))
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
            session['user'] = user.format()
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
    return redirect(url_for('login_page'))

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    else:
        billboard_posts = BillboardPost.query.filter_by(student_id=session['user']['id']).all()
        billboard_posts = [post.format() for post in billboard_posts]
        club_posts = ClubPost.query.filter_by(student_id=session['user']['id']).all()
        club_posts = [post.format() for post in club_posts]
        return render_template('user/profile.html', billboard_posts=billboard_posts, club_posts=club_posts)

@app.route('/update-dp', methods=['POST'])
def update_dp():
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
    data = request.form.to_dict()
    print(data)
    return 'pass'

# BillBoard Routes ------------------------------------------------------------
@app.route('/billboard')
def billboard_page():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    else:
        return render_template('billboard/billboard.html', billboard=get_billboard_posts())


# Club Routes ---------------------------------------------------------------
@app.route('/clubs')
def club():
    return render_template('club/clubs.html', clubs=get_clubs())

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
    data = request.form.to_dict()
    file = request.files['file']
    try:
        # Uploading to cloudinary
        if file.content_type not in ALLOWED_TYPES:
            flash("Invalid image type. Please upload a jpeg or png image.")
            return redirect(request.url)
        res = _cu.upload(file, folder=CLUB_IMG_PATH)
        club = Club(name=data['name'], description=data['description'], school_id=session['user']['school_id'], img_url=res['secure_url'])
        club.insert()
        flash('Club created successfully!')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('Something went wrong!')
        return redirect(url_for('home'))

@app.route('/club-post/<club_id>', methods=['POST'])
def add_club_post(club_id):
    data = request.form.to_dict()
    club_post = ClubPost(title=data['title'], content=data['content'], club_id=club_id, student_id=session['user']['id'])
    club_post.insert()
    flash('Club post created successfully!')
    return redirect(request.referrer)
# ----------------------------------------------------------------------------

@app.route('/shop')
def get_shop_page():
    return render_template('shop/shop.html')

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


@app.route('/events')
def getEvents():
    events = Event.query.all()
    for e in events:
        e.date_time=e.date_time.strftime("%b %d")
        
    return render_template('event.html',events=events)

@app.route('/addevent')
def addEvent():
    schools = [school.format() for school in School.query.all()]
    students = [student.format() for student in Student.query.all()]
    
    return render_template('addEvent.html',schools=schools,students=students)

    

@app.route('/insertevent' ,methods=['POST'])
def insertEvent():
    name = request.form['name']
    description = request.form['description']
    location= request.form['location']
    date_time=request.form['date_time']
    school = request.form['school']
    student = request.form['student']

    new_event=Event(name=name,description=description,location=location,date_time=date_time,school_id=school,student_id=student)
    new_event.insert()
    return redirect(url_for('getEvents'))

@app.route('/session')
def get_session():
    if 'user' in session:
        return session.get('user')
    else:
        'nothing in session'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
