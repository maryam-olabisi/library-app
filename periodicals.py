from flask import Flask,flash, request, render_template, redirect, url_for, session
from models import *
import uuid
import datetime

allPeriodicals = Periodicals.query.all()

def period_form():
    newsname = request.form.get('newsname')
    day = request.form.get('day')
    month = request.form.get('month')
    year = request.form.get('year')
    headlines = request.form.get('headlines')

    return newsname, day, month, year, headlines

def add_period():
    newsname, day, month, year, headlines = period_form()
    newPeriod = Periodicals(newsname, day, month, year, headlines)
    db.session.add(newPeriod)
    db.session.commit()
    return True

def get_period(id):
    return Periodicals.query.filter_by(id=id).first()

def update_period(id):
    newsname, day, month, year, headlines = period_form()
    period = Periodicals.query.filter_by(id=id).first()
    if period:
        if newsname != period.periodical_name:
            period.periodical_name = newsname
        if day != period.periodical_day:
            period.periodical_day = day
        if month != period.periodical_month:
            period.periodical_month = month
        if year != period.periodical_year:
            period.periodical_year = year
        if headlines != period.periodical_details:
            period.periodical_details = headlines
        db.session.commit()
        return True, period
    else:
        return False, "False"

