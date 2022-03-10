from multiprocessing import Event
from unicodedata import name
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                    session, url_for, send_file)
import json
from models import Student, School, Admin, db_init, Event
from passlib.hash import pbkdf2_sha256 as sha256
from mock_data import billboard, events, clubs

app = Flask(__name__)
app.secret_key = 'super secret key'
db = db_init(app)

@app.route('/')
def home():
    if 'user' not in session:
        return render_template('login/login.html')
    else:
        events = Event.query.all()
        return render_template('index.html', billboard=billboard, events=events, clubs=clubs)

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
        print(request.form)
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
                    new_user = Student(id=school_id, name=name, password=sha256.hash(password), bio='', dob='', school_id=school.id)
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
        return render_template('user/profile.html')

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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
