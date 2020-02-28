from flask import Flask,flash, request, render_template, redirect, url_for, session
from models import *
import uuid
import datetime

def get_form():
    number = request.form.get('luser')
    dept = request.form.get('staff')
    return number, dept

def filter_user():
    number, dept = get_form()
    if number:
        found_user = User.query.filter_by(user_phone_number=number).first()
        if not found_user:
            return False, "Number", None
        else:
            return True, "Number", found_user
    elif dept:
        found_users = User.query.filter_by(user_dept=dept).all()
        return True, "Dept", found_users
    else:
        return False, False, False

def get_single_user(id):
    found_user = User.query.filter_by(user_phone_number=id).first()
    if found_user:
        return True, found_user
    else:
        return False, "User Not Found"

def update_user(u_id):
    name = request.form.get('name')
    userid = request.form.get('userid')
    phone = request.form.get('phone')
    email = request.form.get('email')
    dept = request.form.get('dept')
    admin = request.form.get('admin')

    found_user = User.query.filter_by(id=u_id).first()
    if not found_user:
        return False, found_user, False
    else:
        try:
            if found_user.user_name != name:
                found_user.user_name = name
            if found_user.user_id != userid:
                found_user.user_id = userid
            if found_user.user_phone_number != phone:
                found_user.user_phone_number = phone
            if found_user.user_mail != email:
                found_user.user_mail = email
            if found_user.user_dept != dept:
                found_user.user_dept = dept
            if found_user.admin != int(admin):
                found_user.admin = int(admin)
            db.session.commit()
            return True, found_user, True
        except Exception as e:
            return False, found_user, e