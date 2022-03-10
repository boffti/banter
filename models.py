from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Init for main app
def db_init(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    # migrate = Migrate(app, db)
    return db

# Init for Test Suite
def setup_db(app, database_path):
    '''binds a flask application and a SQLAlchemy service'''
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

def db_drop_and_create_all():
    '''drops the database tables and starts fresh
    can be used to initialize a clean database
    '''
    db.drop_all()
    db.create_all()

class Student(db.Model):
    __tabelname__ = 'student'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    password = db.Column(db.String)
    bio = db.Column(db.String)
    dob = db.Column(db.String)
    school_id = db.Column(db.String, db.ForeignKey('school.id'))

    school = db.relationship('School', back_populates='student')

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'bio': self.bio,
            'dob': self.dob,
            'school_id': self.school_id,
            'school': self.school.format()
        }

class School(db.Model):
    __tablename__ = 'school'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    state = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)

    student = db.relationship('Student', back_populates='school', uselist=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'city': self.city,
            'country': self.country
        }

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    school_id = db.Column(db.String, db.ForeignKey('school.id'))

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    date_time = db.Column(db.DateTime)
    location = db.Column(db.String)
    school_id = db.Column(db.String, db.ForeignKey('school.id'))
    student_id  = db.Column(db.String, db.ForeignKey('student.id'))

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
