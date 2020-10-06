from flask import Flask,flash, request, render_template, redirect, url_for, session
from models import *
import uuid
import datetime

allPeriodicals = Periodicals.query.all()

def user_info():
    phone_number = request.form.get('luser')
    found_user = User.query.filter_by(user_phone_number=phone_number).first()
    if found_user:
        return True, found_user
    else:
        return False, "User Not Found"

def trans_list(id):
    found_list = Transaction.query.filter_by(user_id=id).all()
    if found_list:
        return True, found_list
    else:
        return False, "No Transactions Found"

def trans_list_user(id):
    id_use = User.query.get(int(id))
    return trans_list(id_use.user_id), id_use

def reserve_book(id, user_name):
    book = Book.query.filter_by(book_id=id).first()
    book_name = book.book_name
    if not book_name:
        return False
    try:
        new_reserve = Reservations(user_name, datetime.datetime.now(), book_name)
        new_reserve.reserve_status = False
        db.session.add(new_reserve)
        db.session.commit()
        return True
    except expression as identifier:
        return False

def book_info():
    book_name = request.form.get('arrival')
    book = Book.query.filter_by(book_name=book_name).first()
    authors = ""
    subjects = ""
    if book:
        #author
        bookAuthor = book.writers
        for a in bookAuthor:
            if authors == "":
                authors = a.author_name
            else:
                authors += (", " + a.author_name)
        #subj
        bookSubject = book.subjects
        for b in bookSubject:
            if subjects == "":
                subjects = b.subject_name
            else:
                subjects += (", " + b.subject_name)
        return True, book, authors, subjects
    else:
        return False, "False", 0, 0

def borrows(bookid, userid):
    found_book = Book.query.filter_by(book_id=bookid).first()
    #check book availability
    if found_book.book_avail_copies == 0:
        return False, "No Copies Left To Borrow"
    else:
        new_trans = Transaction(bookid, 0, datetime.datetime.now() + datetime.timedelta(weeks=1), userid, datetime.datetime.now())
        db.session.add(new_trans)
        found_book.book_avail_copies -= 1
        db.session.commit()
        return True

def borrow():
    userid = session.get('searched_user', None)
    bookid = session.get('searched_book', None)
    found_book = Book.query.filter_by(book_id=bookid).first()
    #check book availability
    if found_book.book_avail_copies == 0:
        return False, "No Copies Left To Borrow"
    else:
        new_trans = Transaction(bookid, 0, datetime.datetime.now() + datetime.timedelta(weeks=1), userid, datetime.datetime.now())
        db.session.add(new_trans)
        found_book.book_avail_copies -= 1
        db.session.commit()
        return True

def return_books(tid):
    found_trans = Transaction.query.filter_by(id=tid).first()
    found_book = Book.query.filter_by(book_id=found_trans.book_id).first()
    if found_trans:
        found_trans.trans_return_date = datetime.datetime.now()
        found_trans.trans_status = 1
        found_book.book_avail_copies += 1
        db.session.commit()
        return True
