from flask_sqlalchemy import SQLAlchemy
import arrow

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
    major = db.Column(db.String)
    phone = db.Column(db.String)
    dob = db.Column(db.String)
    dp = db.Column(db.String)
    school_id = db.Column(db.String, db.ForeignKey('school.id'))

    school = db.relationship('School', back_populates='student')
    billboard_post = db.relationship('BillboardPost', back_populates='student')
    club_post = db.relationship('ClubPost', back_populates='student')
    event = db.relationship('Event', back_populates='student')
    user_roles = db.relationship('UserRoles', back_populates='student')
    clubs = db.relationship('Club', secondary='club_members', backref='clubs')
    products = db.relationship('Product', back_populates='seller')
    payment_methods = db.relationship('PaymentMethod', back_populates='student')

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
            'major': self.major,
            'phone': self.phone,
            'dob': self.dob,
            'dp': self.dp,
            'school_id': self.school_id,
            'school': self.school.format(),
            'clubs': [club.format2() for club in self.clubs],
        }

class School(db.Model):
    __tablename__ = 'school'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    state = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)

    student = db.relationship('Student', back_populates='school', uselist=False)
    club = db.relationship('Club', back_populates='school', uselist=False)
    billboard_post = db.relationship('BillboardPost', back_populates='school')
    event = db.relationship('Event', back_populates='school', uselist=False)
    products = db.relationship('Product', back_populates='school')
    messages = db.relationship('BroadcastMessage', back_populates='school', uselist=False)

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

class Club(db.Model):
    __tablename__ = 'club'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    img_url = db.Column(db.String)
    school_id = db.Column(db.String, db.ForeignKey('school.id'))
    owner_id = db.Column(db.String, db.ForeignKey('student.id'))

    school = db.relationship('School', back_populates='club')
    club_post = db.relationship('ClubPost', back_populates='club')
    members = db.relationship('Student', secondary='club_members', backref='members')

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
            'description': self.description,
            'img_url': self.img_url,
            'school_id': self.school_id,
            'school': self.school.format(),
            'members': [member.format() for member in self.members]
        }
    def format2(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'img_url': self.img_url,
            'school_id': self.school_id,
            'school': self.school.format(),
        }


class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    date_time = db.Column(db.DateTime)
    location = db.Column(db.String)
    school_id = db.Column(db.String, db.ForeignKey('school.id'))
    student_id  = db.Column(db.String, db.ForeignKey('student.id'))

    student = db.relationship('Student', back_populates='event')
    school = db.relationship('School', back_populates='event')

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
            'description': self.description,
            'date_time': self.date_time,
            'location': self.location,
            'school_id': self.school_id,
            'student_id': self.student_id,
            'student': self.student.format(),
        }

class ClubPost(db.Model):
    __tablename__ = 'club_post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    club_id = db.Column(db.String, db.ForeignKey('club.id'))
    student_id = db.Column(db.String, db.ForeignKey('student.id'))

    club = db.relationship('Club', back_populates='club_post')
    student = db.relationship('Student', back_populates='club_post')

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
            'title': self.title,
            'content': self.content,
            'club_id': self.club_id,
            'club': self.club.format(),
            'student_id': self.student_id,
            'student': self.student.format()
        }

class BillboardPost(db.Model):
    __tablename__ = 'billboard_post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    img_url = db.Column(db.String)
    school_id = db.Column(db.String, db.ForeignKey('school.id'))
    student_id = db.Column(db.String, db.ForeignKey('student.id'))
    tag_id = db.Column(db.String, db.ForeignKey('billboard_categories.id'))
    created_at = db.Column(db.DateTime)

    school = db.relationship('School', back_populates='billboard_post')
    student = db.relationship('Student', back_populates='billboard_post')
    tag = db.relationship('BillboardCategories', back_populates='billboard_post')

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
            'title': self.title,
            'content': self.content,
            'img_url': self.img_url,
            'school_id': self.school_id,
            'student_id': self.student_id,
            'student': self.student.format(),
            'tag_id': self.tag_id,
            'tag': self.tag.format(),
            'created_at': arrow.Arrow.fromdatetime(self.created_at).humanize()
        }

class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String, db.ForeignKey('student.id'))
    role_id = db.Column(db.Integer)

    student = db.relationship('Student', back_populates='user_roles')

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
            'student_id': self.student_id,
            'role_id': self.role_id,
            'user': self.user.format(),
        }

class ClubMembers(db.Model):
    __tablename__ = 'club_members'
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.String, db.ForeignKey('club.id'))
    student_id = db.Column(db.String, db.ForeignKey('student.id'))

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
            'club_id': self.club_id,
            'student_id': self.student_id,
            'club': self.club.format(),
            'student': self.student.format()
        }

class BillboardCategories(db.Model):
    __tablename__ = 'billboard_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    billboard_post = db.relationship('BillboardPost', back_populates='tag')

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
        }

class Advertisement(db.Model):
    __tablename__ = 'advertisement'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    img_url = db.Column(db.String)
    ext_link = db.Column(db.String)
    school_id = db.Column(db.String, db.ForeignKey('school.id'))
    admin_id = db.Column(db.String, db.ForeignKey('student.id'))

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
            'title': self.title,
            'description': self.description,
            'img_url': self.img_url,
            'ext_link': self.ext_link,
            'school_id': self.school_id,
            'admin_id': self.admin_id,
            'tag':'ad'
        }
    
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    price = db.Column(db.Float)
    img_url = db.Column(db.String)
    school_id = db.Column(db.String, db.ForeignKey('school.id'))
    seller_id = db.Column(db.String, db.ForeignKey('student.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    created_at = db.Column(db.DateTime)
    purchased = db.Column(db.Boolean)

    school = db.relationship('School', back_populates='products')
    seller = db.relationship('Student', back_populates='products')
    category = db.relationship('ProductCategory', back_populates='products')
    order = db.relationship('Order', back_populates='product')

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
            'title': self.title,
            'description': self.description,
            'img_url': self.img_url,
            'ext_link': self.ext_link,
            'school_id': self.school_id,
            'admin_id': self.admin_id,
            'tag': 'ad',
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'img_url': self.img_url,
            'student': self.student.format(),
            'category': self.category_id.format(),
            'created_at': arrow.Arrow.fromdatetime(self.created_at).humanize()
        }

class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    products = db.relationship('Product', back_populates='category')

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
        }

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    seller_id = db.Column(db.String, db.ForeignKey('student.id'))
    buyer_id = db.Column(db.String, db.ForeignKey('student.id'))
    created_at = db.Column(db.DateTime)

    seller = db.relationship('Student', backref='orderss', foreign_keys=[seller_id])
    buyer = db.relationship('Student', backref='orders', foreign_keys=[buyer_id])
    product = db.relationship('Product', back_populates='order')

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
            'product_id': self.product_id,
            'seller_id': self.seller_id,
            'buyer_id': self.buyer_id,
            'created_at': arrow.Arrow.fromdatetime(self.created_at).humanize()
        }

class BroadcastMessage(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    created_at = db.Column(db.DateTime)
    school_id = db.Column(db.String, db.ForeignKey('school.id'))

    school = db.relationship('School', back_populates='messages')

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
            'title': self.title,
            'content': self.content,
            'school_id': self.school_id,
            'created_at': arrow.Arrow.fromdatetime(self.created_at).humanize()
        }

class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String, db.ForeignKey('student.id'))
    card_number = db.Column(db.String)
    name_on_card = db.Column(db.String)
    valid_through = db.Column(db.DateTime)
    cvv = db.Column(db.Integer)
    zip_code = db.Column(db.Integer)

    student = db.relationship('Student', back_populates='payment_methods')

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
            'description': self.description,
            'school_id': self.school_id,
        }