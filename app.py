from flask import Flask,flash, request, render_template, redirect, url_for, session
from models import *
from authentication import *
from department import *
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

@app.route('/adddept', methods=['POST'])
@login_required
def addDept():
    email = current_user.user_mail
    status, result = add_dept()
    dept_success = ""
    dept_error = ""
    allDepts = Department.query.all()
    if status:
        # true
        dept_success = "Department Successfully Added"
    else:
        #repeat
        dept_error = "Department Name Already Exists"
    return render_template('admin.html',  email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks, dept_success=dept_success, dept_error=dept_error)

@app.route('/addsubj', methods=['POST'])
@login_required
def addSubj():
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

@app.route('/addpub', methods=['POST'])
@login_required
def addPub():
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

@app.route('/register', methods=['POST'])
def register():
    status = register_user()
    if status is True:
        success = "Pre-Registration Successful. Please Visit the Library to Complete Your Registration."
        return render_template('login.html', allDepts=allDepts, success=success)
    else:
        error = "Registration Error. Your ID Number, Phone Number And/Or Email Address Have Been Previously Registered. Please Log In Or Visit the Library to Complete Registration."
        return render_template('login.html', allDepts=allDepts, error=error)


# @app.route('/oaccess', methods=['GET','POST'])
# def oaccess():
#     return render_template('oaccess.html')

# @app.route('/caccess', methods=['GET'])
# def table():
#     return render_template('caccess.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)