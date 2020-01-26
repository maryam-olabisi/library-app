from flask import Flask,flash, request, render_template, redirect, url_for, session
from models import *
import datetime

def new_author():
    name = request.form.get('authorname')
    try:
        authExists = Author.query.filter_by(author_name=name).first()
        if not authExists:
            newAuthor = Author(name)
            db.session.add(newAuthor)
            db.session.commit()
            return True
        else:
            return False
    except exc.IntegrityError:
        return False

def new_publisher():
    name = request.form.get('pubname')
    address = request.form.get('pubadd')
    try:
        pubExists = Publisher.query.filter_by(pub_name=name,pub_address=address).first()
        if not pubExists:
            newPub = Publisher(name, address)
            db.session.add(newPub)
            db.session.commit()
            return True
        else:
            return False
    except exc.IntegrityError:
        return False
    except exc.InvalidRequestError:
        return False

###new subject
def add_subj():
    name = request.form.get('subjname')
    try:
        newSubj = Subject(name)
        db.session.add(newSubj)
        db.session.commit()
        return True
    except exc.IntegrityError:
        return False
    except exc.InvalidRequestError:
        return False

###new dept
def add_dept():
    name = request.form.get('deptname')
    try:
        newDept = Department(name) 
        db.session.add(newDept)
        db.session.commit()
        return True, newDept
    except exc.IntegrityError:
        return False, "False"
    except exc.InvalidRequestError:
        db.session.rollback()
        return False, "False"

###selected


###update