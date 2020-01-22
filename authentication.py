from flask import Flask,flash, request, render_template, redirect, url_for, session
from models import *
import datetime


#register middleware
def formdata():
    #id, name, dept, phone, email 
    user_id = request.form.get('userid')
    user_name = request.form.get('name')
    dept = request.form.get('ldepartment')
    phone = request.form.get('phone')
    email = request.form.get('email')

    return user_id, user_name, dept, phone, email

def register_user():
    user_id, user_name, dept, phone, email = formdata()
    #check if dept exists
    deptExist = Department.query.filter_by(dept_name=dept).first()
    dept_id = ""
    if deptExist:
        #get id
        dept_id = deptExist.id
    else:
        #add and get id
        newDept = Department(dept)
        db.session.add(newDept)
        db.session.commit()
        dept_id = newDept.id
    #add user to db
    try:
        user = User(user_id, user_name, phone, dept_id, email, False)
        db.session.add(user)
        db.session.commit()
        return True
    except exc.IntegrityError:
        return False

# login middleware
def login_data():
    username = request.form.get('userid')
    password = request.form.get('password')
    return username, password
    
def signin_user():
    userid, phone = login_data()
    userExists = User.query.filter_by(user_id=userid).first()
    if userExists:
        # ?compare phone number
        if (userExists.user_phone_number == phone):
            return True, userExists
        else:
            return False, "False"
    else:
        return False, "False"