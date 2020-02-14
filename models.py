from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy import exc, text 
import jwt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask("__name__")
app.config.from_object('settings')
# app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)

migrate = Migrate(app,db)
manager = Manager(app,db)
manager.add_command('db', MigrateCommand)

class Periodicals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    periodical_name =  db.Column(db.String(500), unique=False)
    periodical_day = db.Column(db.String(5), unique=False)
    periodical_month = db.Column(db.String(5), unique=False)
    periodical_year = db.Column(db.String(5), unique=False)
    periodical_details = db.Column(db.String(2500), unique=False)

    def __init__(self, periodical_name, periodical_day, periodical_month, periodical_year, periodical_details):
        self.periodical_name = periodical_name
        self.periodical_day = periodical_day
        self.periodical_year = periodical_year
        self.periodical_month = periodical_month
        self.periodical_details = periodical_details

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String(25), unique=True)
    book_name =  db.Column(db.String(500), unique=False)
    book_source = db.Column(db.String(500), unique=False)
    book_date = db.Column(db.String(10), unique=False)
    book_isbn = db.Column(db.String(500), unique=False)
    book_call_no = db.Column(db.String(500), unique=False)
    book_pagination = db.Column(db.String(500), unique=False)
    book_notes = db.Column(db.String(900), unique=False)
    book_assession_no = db.Column(db.String(500), unique=False)
    book_total_copies = db.Column(db.Integer, unique=False)
    book_avail_copies = db.Column(db.Integer, unique=False)

    pub_id = db.Column(db.Integer, db.ForeignKey('publisher.id'), unique=False)
    borrowed_books = db.relationship('Transaction', backref='book', lazy='dynamic')

    def __init__(self, book_name, book_source, book_date, book_isbn, book_call_no, book_pagination, book_notes, book_assession_no, book_total_copies):
        self.book_name = book_name
        self.book_source = book_source
        self.book_date = book_date
        self.book_isbn = book_isbn
        self.book_call_no = book_call_no
        self.book_pagination = book_pagination
        self.book_notes = book_notes
        self.book_assession_no = book_assession_no
        self.book_total_copies = book_total_copies

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id =  db.Column(db.String(50), unique=True)
    user_name =  db.Column(db.String(500), unique=False)
    user_phone_number =  db.Column(db.String(15), unique=True)
    user_mail = db.Column(db.String(250), unique=True)
    user_dept = db.Column(db.Integer, db.ForeignKey('department.id'), unique=False)
    admin = db.Column(db.Boolean, unique=False)
    
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    
    def __init__(self, user_id, user_name, user_phone_number, user_dept, user_mail, admin):
        self.user_id = user_id
        self.user_name = user_name
        self.user_phone_number = user_phone_number
        self.user_dept = user_dept
        self.user_mail = user_mail
        self.admin = admin

    def is_authenticated(self):
        return self.authenticated
    
    def is_active(self):
       return True

class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pub_name =  db.Column(db.String(500), unique=False)
    pub_address =  db.Column(db.String(500), unique=False)

    publishers = db.relationship('Book', backref='publisher', lazy='dynamic')

    def __init__(self, pub_name, pub_address):
        self.pub_name = pub_name
        self.pub_address = pub_address

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dept_name =  db.Column(db.String(500), unique=True)
    departments = db.relationship('User', backref='dept', lazy='dynamic')
    book_dept = db.relationship('Book', secondary='booksbydepartment', backref=db.backref('departments', lazy='dynamic'))

    def __init__(self, dept_name):
        self.dept_name = dept_name

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name =  db.Column(db.String(500), unique=False)
    authors = db.relationship('Book', secondary='collection', backref=db.backref('writers', lazy='dynamic'))

    def __init__(self, author_name):
        self.author_name = author_name

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_name =  db.Column(db.String(500), unique=True)

    book_subject = db.relationship('Book', secondary='booksandsubject', backref=db.backref('subjects', lazy='dynamic'))
    
    def __init__(self, subject_name):
        self.subject_name = subject_name

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trans_date = db.Column(db.DateTime, unique=False)
    trans_status = db.Column(db.Boolean, unique=False)
    trans_due_date = db.Column(db.DateTime, unique=False)
    trans_return_date = db.Column(db.DateTime, unique=False)

    user_id =  db.Column(db.String(25), db.ForeignKey('user.user_id'), unique=False)
    book_id = db.Column(db.String(25), db.ForeignKey('book.book_id'), unique=False)
    
    def __init__(self, book_id, trans_status, trans_due_date, user_id, trans_date):
        self.book_id = book_id
        self.trans_status = trans_status
        self.trans_due_date = trans_due_date
        self.user_id = user_id
        self.trans_date = trans_date

collection = db.Table('collection',
        db.Column('book_id', db.String(25), db.ForeignKey('book.book_id'), unique=False),
        db.Column('author_id', db.Integer, db.ForeignKey('author.id'), unique=False)
)

booksandsubject = db.Table('booksandsubject',
        db.Column('book_id', db.String(25), db.ForeignKey('book.book_id'), unique=False),
        db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), unique=False)
)

booksbydepartment = db.Table('booksbydepartment',
        db.Column('book_id', db.String(25), db.ForeignKey('book.book_id'), unique=False),
        db.Column('id', db.Integer, db.ForeignKey('department.id'), unique=False)
)

if __name__ == "__main__":
    manager.run()
    # db.create_all()
