from flask import Flask,flash, request, render_template, redirect, url_for, session
from models import *
import uuid
import datetime

#new arrival list
newArrivals = Book.query.filter_by(book_assession_no="").all()

#middleware
def book_form():
    bookname = request.form.get('bookname')
    booksource = request.form.get('booksource')
    bookyear = request.form.get('bookyear')
    pubname = request.form.get('pubname')
    pubadd = request.form.get('pubadd')
    bookcopies = request.form.get('bookcopies')
    author = request.form.get('authors')
    aauthor = request.form.get('aauthors')

    return bookname, booksource, bookyear, pubname, pubadd, bookcopies, author, aauthor

def new_book():
    bookname, booksource, bookyear, pubname, pubadd, bookcopies, author, aauthor = book_form()
    pub_id = ""
    auth_id = []
    bookExists = Book.query.filter_by(book_name=bookname,book_date=bookyear,book_source=booksource,pub_id=pubname).first()
    if bookExists:
        return False, "exists"
    else:
        #check publisher and get publisher id
        pubExists = Publisher.query.filter_by(pub_name=pubname,pub_address=pubadd).first()
        if pubExists:
            pub_id = pubExists.id
        else:
            newPub = Publisher(pubname, pubadd)
            db.session.add(newPub)
            db.session.commit()
            pub_id = newPub.id
        #check author and get author id
        authorExists = Author.query.filter_by(author_name=author).first()
        if authorExists:
            auth_id.append(authorExists)
        else:
            newAuthor = Author(author)
            db.session.add(newAuthor)
            db.session.commit()
            auth_id.append(newAuthor)
        #check supporting author
        sAuthorExists = Author.query.filter_by(author_name=aauthor).first()
        if sAuthorExists:
            auth_id.append(sAuthorExists)
        else:
            newSAuthor = Author(aauthor)
            db.session.add(newSAuthor)
            db.session.commit()
            auth_id.append(newSAuthor)
        #add new arrival
        # try:
        newArrival = Book(bookname, booksource, bookyear, "", "", "", "", "", bookcopies)
        db.session.add(newArrival)
        db.session.commit()
        #update id & available copies
        bookid = str(uuid.uuid4())[:6]
        newArrival.book_id = 'book' + str(newArrival.id) + bookid
        newArrival.book_avail_copies = bookcopies
        #add publisher
        newArrival.pub_id = pub_id
        #add author
        for au in auth_id:
            au.authors.append(newArrival)
        db.session.commit()
        return True
        # except:
        # return False

def select_book():
    id = request.form.get('arrival')
    book = Book.query.filter_by(book_id=id).first()
    authors = ""
    subjects = ""
    mainAuth = 0
    supAuth = 0
    bookSubj = []
    if book:
        #author
        bookAuthor = book.writers
        for a in bookAuthor:
            if authors == "":
                authors = a.author_name
                mainAuth = a.id
            else:
                supAuth = a.id
                authors += (", " + a.author_name)
        #subj
        bookSubject = book.subjects
        for b in bookSubject:
            if subjects == "":
                subjects = b.subject_name
                bookSubj.append(b)
            else:
                subjects += (", " + b.subject_name)
                bookSubj.append(b)
        return True, book, authors, subjects, mainAuth, supAuth, bookSubj
    else:
        return False, "False", 0, 0, 0, 0, 0

def update_form():
    bookname = request.form.get('bookname')
    booksource = request.form.get('booksource')
    bookyear = request.form.get('bookyear')
    pubname = request.form.get('pubname')
    pubadd = request.form.get('pubadd')
    bookcopies = request.form.get('bookcopies')
    author = request.form.get('authors')
    aauthor = request.form.get('aauthors')
    isbn = request.form.get('isbn')
    callno = request.form.get('callno')
    notes = request.form.get('notes')
    bookpages = request.form.get('pagination')
    accession = request.form.get('assessionnumber')
    subjects = request.form.getlist('lsubjects')

    return bookname, booksource, bookyear, pubname, pubadd, bookcopies, author, aauthor, isbn, callno, notes, bookpages, accession, subjects

def update_book(bookid):
    bookname, booksource, bookyear, pubname, pubadd, bookcopies, author, aauthor, isbn, callno, notes, bookpages, accession, subjects = update_form()
    #get book, compare
    book = Book.query.filter_by(book_id=bookid).first()
    publishers = Publisher.query.filter_by(id=book.pub_id).first()
    authList = book.writers
    subjList = book.subjects
    if not book:
        return False
    else:
        if book.book_name != bookname:
            book.book_name = bookname
        if book.book_assession_no != accession:
            book.book_assession_no = accession
        if book.book_total_copies != bookcopies:
            book.book_total_copies = bookcopies
        if book.book_source != booksource:
            book.book_source = booksource
        if book.book_date != bookyear:
            book.book_date = bookyear
        if book.book_isbn != isbn:
            book.book_isbn = isbn
        if book.book_call_no != callno:
            book.book_call_no = callno
        if book.book_pagination != bookpages:
            book.book_pagination = bookpages
        if book.book_notes != notes:
            book.book_notes = notes
        if book.book_assession_no != accession:
            book.book_assession_no = accession
        if (publishers.pub_name != pubname) or (publishers.pub_address != pubadd):
            idPub = Publisher.query.filter_by(pub_name=pubname,pub_address=pubadd).first()
            book.pub_id = idPub.id
        
        authList = []
        authId = Author.query.filter_by(id=int(author)).first()
        authList.append(authId)
        exAuth = authId.author_name
        sauthIds = 0
        if aauthor != 0:
            sAuthId = Author.query.filter_by(id=int(aauthor)).first()
            sauthIds = sAuthId.id
            authList.append(sAuthId)
            exAuth += (", " + sAuthId.author_name)
        
        subjList = []
        exSub = ""
        for s in subjects:
            sub = Subject.query.filter_by(id=s).first()
            subjList.append(sub)
            if exSub == "":
                exSub = sub.subject_name
            else:
                exSub += ", " + sub.subject_name
        db.session.commit()
        # if author != authList[0].author_name:
        #     authid = Author.query.filter_by(author_name=author).first()
        #     authList[0].author_id = authid
        # if aauthor == "":
        #     toRemove = Author.query.filter_by(author_name=aauthor).first()
        #     authList.remove(toRemove)
        # elif aauthor != authList[1].author_name:
        #     authid = Author.query.filter_by(author_name=aauthor).first()
        #     authList[1].author_id = authid
    return True, book, exAuth, exSub, authId.id, sauthIds, subjList
