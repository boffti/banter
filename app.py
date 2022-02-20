from flask import (Flask, flash, jsonify, redirect, render_template, request,
                    session, url_for, send_file)
import json
from models import Student, School, Admin, db_init

app = Flask(__name__)
db = db_init(app)

@app.route('/')
def home():
    if 'user' not in session:
        return render_template('login/login.html')
    else:
        return render_template('index.html')

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
    return login_creds

# Logout Route
@app.route('/logout')
def logout():
    # Remove the user from session
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('user_login'))

# Schools dropdown route
@app.route('/schools')
def getRegions():
    schools = School.query.all()
    schoolsResponse = [school.format() for school in schools]
    return json.dumps(schoolsResponse)

@app.route('/test')
def test():
    students = Student.query.all()
    studentResponse = [student.format() for student in students]
    return json.dumps(studentResponse)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
