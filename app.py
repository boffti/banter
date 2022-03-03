from unicodedata import name
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                    session, url_for, send_file)
import json
from models import Student, School, Admin, db_init
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

@app.route('/update-dp', methods=['POST'])
def update_dp():
    dp = request.files['file']
    if dp.filename != '':
        file_name = f'{session["user"]["id"]}.jpg'
        user_id = session['user']['id']
        user = Student.query.filter_by(id=user_id).first()
        user.dp = file_name
        user.update()
        dp.save(f'static/images/dp/{file_name}')
        session['user'] = user.format()
        return '1'
    else:
        return '0'

@app.route('/update-profile')
def update_profile():
    return 'pass'

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
    if 'user' in session:
        return session.get('user')
    else:
        'nothing in session'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
