from flask import Flask,flash, request, render_template, redirect, url_for, session
from models import *
from authentication import *
from department import *
from books import *
import datetime 

app = Flask("__name__")
app.config.from_object('settings')
# app.config.from_pyfile('config.cfg')
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

allDepts = Department.query.all()
allSubj = Subject.query.all()
allAuthors = Author.query.all()
allPubs = Publisher.query.all()
allBooks = Book.query.all()
currentYear = str(datetime.datetime.today().year)

@login_manager.user_loader
def load_user(username):
    return User.query.get(int(username))

@app.route('/')
def homepage():
    return render_template('home.html', currentYear=currentYear, allDepts=allDepts)

@app.route('/login', methods=['GET','POST'])
def login():
    logout_user()
    if (request.method=='POST'):
        status, staff = signin_user()
        if status:
            login_user(staff)
            return redirect(url_for('admin'))
            # return render_template('admin.html', allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)
        else:
            errorM = "One of given fields is Incorrect. Try Again."
            return render_template('login.html', errorM=errorM, allDepts=allDepts, currentYear=currentYear)
    return render_template('login.html', allDepts=allDepts, currentYear=currentYear)

@app.route('/admin', methods=['GET','POST'])
@login_required
def admin():
    email = current_user.user_mail
    return render_template('admin.html',  email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)

@app.route('/adddept', methods=['GET','POST'])
@login_required
def addDept():
    if (request.method=='POST'):
        email = current_user.user_mail
        status, result = add_dept()
        msg_success = ""
        msg_error = ""
        allDepts = Department.query.all()
        if status:
            # true
            msg_success = "Department Successfully Added"
        else:
            #repeat
            msg_error = "Department Name Already Exists"
        return render_template('admin.html',  email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks, msg_success=msg_success, msg_error=msg_error)
    return redirect(url_for('admin'))

@app.route('/addsubj', methods=['GET','POST'])
@login_required
def addSubj():
    if (request.method=='POST'):
        email = current_user.user_mail
        status = add_subj()
        msg_success = ""
        msg_error = ""
        allSubj = Subject.query.all()
        if status:
            # true
            msg_success = "Subject Successfully Added"
        else:
            #repeat
            msg_error = "Subject Name Already Exists"
        return render_template('admin.html', email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks, msg_error=msg_error, msg_success=msg_success)
    return redirect(url_for('admin'))

@app.route('/addpub', methods=['GET','POST'])
@login_required
def addPub():
    if (request.method=='POST'):
        email = current_user.user_mail
        status = new_publisher()
        msg_success = ""
        msg_error = ""
        allPubs = Publisher.query.all()
        if status:
            # true
            msg_success = "Publisher Successfully Added"
        else:
            #repeat
            msg_error = "Publisher's Details Already Exists"
        return render_template('admin.html', email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks, msg_error=msg_error, msg_success=msg_success)
    return redirect(url_for('admin'))

@app.route('/addauthor', methods=['GET','POST'])
@login_required
def addAuthor():
    if (request.method=='POST'):
        email = current_user.user_mail
        status = new_author()
        msg_success = ""
        msg_error = ""
        allAuthors = Author.query.all()
        if status:
            # true
            msg_success = "Author Successfully Added"
        else:
            #repeat
            msg_error = "Author's Name Already Exists"
        return render_template('admin.html', email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks, msg_error=msg_error, msg_success=msg_success)
    return redirect(url_for('admin'))

@app.route('/getdept')
@login_required
def getdept():
    return render_template('index.hrml')

@app.route('/transactions', methods=['GET','POST'])
def trans():
    return render_template('transaction.html', allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)

@app.route('/books', methods=['GET','POST'])
@login_required
def addBook():
    email = current_user.user_mail
    allSubj = Subject.query.all()
    if (request.method =='POST'):
        status = new_book()
        msg_success = ""
        msg_error = ""
        if status:
            # true
            msg_success = "New Arrival Successfully Added"
        else:
            #repeat
            msg_error = "Arrival Already Registered, Please Update Instead"
        return render_template('books.html', email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks, msg_error=msg_error, msg_success=msg_success, newArrivals=newArrivals)
    return render_template('books.html', email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks, newArrivals=newArrivals)

@app.route('/getbook', methods=['GET','POST'])
@login_required
def getBook():
    if (request.method =='POST'):
        email = current_user.user_mail
        allSubj = Subject.query.all()
        status, book, bookauthor, booksubj, mainAuth, supAuth, bookSubjList = select_book()
        msg_success = ""
        msg_error = ""
        if status:
            # book found
            return render_template('editbooks.html', bookauthor=bookauthor, bookSubjList=bookSubjList, booksubj=booksubj, mainAuth=mainAuth, supAuth=supAuth, email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks, msg_error=msg_error, msg_success=msg_success, newArrivals=newArrivals, book=book)
        else:
            #not found
            msg_error = "Book Not Found"
            return render_template('books.html', email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks, msg_error=msg_error, msg_success=msg_success, newArrivals=newArrivals)
    return redirect(url_for('addBook'))

@app.route('/editbook/<book_id>', methods=['GET','POST'])
@login_required
def updateBook(book_id):
    if (request.method=='POST'):
        email = current_user.user_mail
        allSubj = Subject.query.all()
        status, book, bookauthor, booksubj, mainAuth, supAuth, bookSubjList = update_book(book_id)
        msg_success = ""
        msg_error = ""
        if status:
            #final
            msg_success = "Book Updated Successfully"
            return render_template('editbooks.html', bookauthor=bookauthor, bookSubjList=bookSubjList, booksubj=booksubj, mainAuth=mainAuth, supAuth=supAuth, email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks, msg_error=msg_error, msg_success=msg_success, newArrivals=newArrivals, book=book)
        else:
            msg_error = "Error"
            return render_template('editbooks.html', bookauthor=bookauthor, bookSubjList=bookSubjList, booksubj=booksubj, mainAuth=mainAuth, supAuth=supAuth, email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks, msg_error=msg_error, msg_success=msg_success, newArrivals=newArrivals, book=book)
    return redirect(url_for('addBook'))

@app.route('/details', methods=['GET','POST'])
@login_required
def details():
    email = current_user.user_mail
    allSubj = Subject.query.all()
    return render_template('details.html', email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)

@app.route('/register', methods=['POST'])
def register():
    status = register_user()
    if status is True:
        success = "Pre-Registration Successful. Please Visit the Library to Complete Your Registration."
        return render_template('login.html', allDepts=allDepts, success=success)
    else:
        error = "Registration Error. Your ID Number, Phone Number And/Or Email Address Have Been Previously Registered. Please Log In Or Visit the Library to Complete Registration."
        return render_template('login.html', allDepts=allDepts, error=error)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
