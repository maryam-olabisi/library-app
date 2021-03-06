from flask import Flask,flash, request, render_template, redirect, url_for, session, json, jsonify
from models import *
from authentication import *
from department import *
from books import *
from staff import *
from periodicals import *
from transactions import *
import datetime 

app = Flask("__name__")
app.config.from_object('settings')
# app.config.from_pyfile('config.cfg')
# db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

allDepts = Department.query.all()
allUsers = User.query.all()
allSubj = Subject.query.all()
allAuthors = Author.query.all()
allPubs = Publisher.query.all()
allBooks = Book.query.all()
allPeriodicals = Periodicals.query.all()
allTransactions = Transaction.query.all()
currentYear = str(datetime.datetime.today().year)

@login_manager.user_loader
def load_user(username):
    return User.query.get(int(username))

def admin_required(f):
    @wraps(f)
    def is_admin(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin:
            logout_user()
            session['adminerror'] = "UNAUTHORIZED ACTION. LOG IN AGAIN"
            return redirect(url_for('login'))
        else:
            return f(*args, **kwargs)
    return is_admin

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html', currentYear=currentYear, allDepts=allDepts)

@app.route('/')
def homepage():
    return render_template('home.html', currentYear=currentYear, allDepts=allDepts)

@app.route('/library-rules')
def rules():
    return render_template('rules.html', currentYear=currentYear, allDepts=allDepts)

@app.route('/login', methods=['GET','POST'])
def login():
    logout_user()
    admin_error_msg = session.get('adminerror', None)
    if (request.method=='POST'):
        status, staff = signin_user()
        if status:
            login_user(staff)
            if staff.admin:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('view_books'))
            # return render_template('admin.html', allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)
        else:
            errorM = "One of given fields is Incorrect. Try Again."
            return render_template('login.html', errorM=errorM, allDepts=allDepts, currentYear=currentYear)
    return render_template('login.html', allDepts=allDepts, currentYear=currentYear, admin_error_msg=admin_error_msg)

@app.route('/admin', methods=['GET','POST'])
@login_required
@admin_required
def admin():
    email = current_user.user_mail
    return render_template('admin.html',  email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)

@app.route('/user/<id>', methods=['POST'])
@login_required
@admin_required
def post_single_user(id):
    # return "POST"
    status, found_user, e = update_user(id)
    if not status:
        db.session.rollback()
        msg_error = ""
        if e:
            msg_error = e
        else:
            msg_error = "An Error Occured"
        return render_template('user.html', found_user=found_user, msg_error=msg_error, currentYear=currentYear, allDepts=allDepts, allUsers=allUsers)
    else:
        msg_success = "User Details Updated"
        return render_template('user.html', found_user=found_user, msg_success=msg_success, currentYear=currentYear, allDepts=allDepts, allUsers=allUsers)


@app.route('/user/<id>', methods=['GET'])
@login_required
@admin_required
def single_user(id):
    status, found_user = get_single_user(id)
    if status:
        return render_template('user.html', found_user=found_user, currentYear=currentYear, allDepts=allDepts, allUsers=allUsers)
    else:
        msg_error=found_user
    return render_template('users.html', msg_error=msg_error, currentYear=currentYear, allDepts=allDepts, allUsers=allUsers)

@app.route('/users', methods=['GET','POST'])
@login_required
@admin_required
def users_info():
    if request.method == "POST":
        status, option, result = filter_user()
        if status:
            if option == "Number":
                return redirect(url_for('single_user', id=result.user_phone_number))
            else:
                filterResults = result
                return render_template('users.html', filterResults=filterResults, currentYear=currentYear, allDepts=allDepts, allUsers=allUsers)
        else:
            if option == "Number":
                msg_error="User NOt Found. Try Again."
            else:
                msg_error = "An Error Occurred. Try Again."
            return render_template('users.html', msg_error=msg_error, currentYear=currentYear, allDepts=allDepts, allUsers=allUsers)
    return render_template('users.html', currentYear=currentYear, allDepts=allDepts, allUsers=allUsers)


@app.route('/adddept', methods=['GET','POST'])
@login_required
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
    return render_template('index.html')

@app.route('/viewbooks', methods=['GET'])
@login_required
def view_books():
    return render_template('allbooks.html', allBooks=allBooks, allPubs=allPubs, currentYear=currentYear, allTransactions=allTransactions, allUsers=allUsers, allAuthors=allAuthors, allSubj=allSubj, allDepts=allDepts, allPeriodicals=allPeriodicals)

@app.route('/transactions/all', methods=['GET','POST'])
@login_required
@admin_required
def all_trans():
    foundTrans = allTransactions
    return render_template('alltrans.html', foundTrans=foundTrans, currentYear=currentYear, allUsers=allUsers)

@app.route('/transactions/<id>', methods=['GET','POST'])
@login_required
@admin_required
def user_trans(id):
    found_trans, found_user = trans_list_user(id)
    foundTrans = found_trans[1]
    lstatus = found_trans[0]
    return render_template('usertrans.html', lstatus=lstatus, foundTrans=foundTrans, found_user=found_user, allUsers=allUsers, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)


@app.route('/reserve/<id>', methods=['GET','POST'])
@login_required
def reserve(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    name = current_user.user_name
    status = reserve_book(id, name)
    if status:
        msg_success = "Book Reserved. Please Visit The Library to Complete Transaction."
        return render_template('allbooks.html', msg_success=msg_success, allBooks=allBooks, allPubs=allPubs, currentYear=currentYear, allTransactions=allTransactions, allUsers=allUsers, allAuthors=allAuthors, allSubj=allSubj, allDepts=allDepts, allPeriodicals=allPeriodicals)
    else:
        msg_error = "Cannot Reserve Book. Visit the University Library for More Information."
        return render_template('allbooks.html',msg_error=msg_error, msg_success=msg_success, allBooks=allBooks, allPubs=allPubs, currentYear=currentYear, allTransactions=allTransactions, allUsers=allUsers, allAuthors=allAuthors, allSubj=allSubj, allDepts=allDepts, allPeriodicals=allPeriodicals)

@app.route('/myreserves', methods=['GET'])
@login_required
def resve():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    username = current_user.user_name
    status = ""
    foundTrans = Reservations.query.filter_by(reserve_name=username).all()
    if foundTrans:
        status = True
    else:
        status = False
    return render_template('myreserves.html', status=status, foundTrans=foundTrans, allAuthors=allAuthors, currentYear=currentYear, allBooks=allBooks, allDepts=allDepts, allSubj=allSubj, allPubs=allPubs)

@app.route('/reservations', methods=['GET','POST'])
@login_required
@admin_required
def adm_rese():
    foundTrans = Reservations.query.all()
    status = ""
    if foundTrans:
        status = True
    else:
        status = False
    return render_template('myreserves.html', status=status, foundTrans=foundTrans, allAuthors=allAuthors, currentYear=currentYear, allBooks=allBooks, allDepts=allDepts, allSubj=allSubj, allPubs=allPubs)

@app.route('/transactions', methods=['GET','POST'])
@login_required
@admin_required
def trans():
    session.pop('searched_user', None)
    session.pop('searched_book', None)
    if (request.method=='POST'):
        email = current_user.user_mail
        msg_error = ""
        status, found_user = user_info()
        if status:
            session['searched_user'] = found_user.user_id
            lstatus, ltrans = trans_list(found_user.user_id)
            session['searched_status'] = lstatus
            return render_template('transaction.html', found_user=found_user, lstatus=lstatus, ltrans=ltrans, email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)
        else:
            msg_error = found_user
            return render_template('transaction.html', msg_error=msg_error, email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)
    return render_template('transaction.html', allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)

@app.route('/bookTrans', methods=['GET','POST'])
@login_required
@admin_required
def book_trans():
    userid = session.get('searched_user', None)
    found_user = User.query.filter_by(user_id=userid).first()
    lstatus, ltrans = trans_list(found_user.user_id)
    session.pop('searched_trans', None)
    email = current_user.user_mail
    # categoryexists = session.get('added_category', None)
    if request.method == 'POST':
        msg_error = ""
        status, book, authors, subjects = book_info()
        if status:
            session['searched_book'] = book.book_id
            return render_template('transaction.html', authors=authors, book=book, subjects=subjects, found_user=found_user, lstatus=lstatus, ltrans=ltrans, email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)
        else:
            msg_error = "Book Not Found"
            return render_template('transaction.html', msg_error=msg_error, found_user=found_user, lstatus=lstatus, ltrans=ltrans, email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)
    return render_template('transaction.html', found_user=found_user, lstatus=lstatus, ltrans=ltrans, email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)

@app.route('/confirmborrow', methods=['GET','POST'])
@login_required
@admin_required
def confirm_borrow():
    # if request.method == 'POST':
    # return "BORROWS"
    status = borrow()
    msg_error=""
    msg_success=""
    if status:
        msg_success = "Book Borrow Process Successful"
        return render_template('transaction.html', msg_success=msg_success, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)
    else:
        msg_error = "Error Occurred. Process Cancelled. There Could be No Copies Left to Borrow"
        return render_template('transaction.html', msg_error=msg_error, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)
    # return redirect(url_for('trans'))

@app.route('/confirmreturn/<tid>', methods=['GET','POST'])
@login_required
@admin_required
def confirm_return(tid):
    # if request.method == 'POST':
    status = return_books(tid)
    msg_error=""
    msg_success=""
    if status:
        msg_success = "Book Return Process Successful"
        return render_template('transaction.html', msg_success=msg_success, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)
    else:
        msg_error = "Error Occurred. Process Cancelled."
        return render_template('transaction.html', msg_error=msg_error, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)
    # return redirect(url_for('trans'))

@app.route('/books', methods=['GET','POST'])
@login_required
@admin_required
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
@admin_required
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

@app.route('/books/<book_id>', methods=['GET','POST'])
@login_required
def user_books_list(book_id):
    status, book, bookauthor, booksubj, mainAuth, supAuth, bookSubjList = select_book(book_id)
    msg_success = ""
    msg_error = ""
    if status:
        return render_template('editbooks.html', bookauthor=bookauthor, bookSubjList=bookSubjList, booksubj=booksubj, mainAuth=mainAuth, supAuth=supAuth, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks, msg_error=msg_error, msg_success=msg_success, newArrivals=newArrivals, book=book)
    else:
        msg_error = "Book Not Found"
    if request.method == "POST":
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
    return render_template('allbooks.html', msg_error=msg_error, allBooks=allBooks, currentYear=currentYear)

@app.route('/editbook/<book_id>', methods=['GET','POST'])
@login_required
@admin_required
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
@admin_required
def details():
    email = current_user.user_mail
    allSubj = Subject.query.all()
    return render_template('details.html', email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)

@app.route('/viewperiodicals', methods=['GET','POST'])
@login_required
def mytrans():
    return render_template('periodicals.html', allPeriodicals=allPeriodicals, lMonth=lMonth, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)

@app.route('/viewperiodicals/<id>', methods=['GET'])
@login_required
def mytransc(id):
    period = get_period(id)
    msg_error = ''
    if period is None:
        msg_error = "Periodical Not Found"
        return render_template('periodicals.html', allPeriodicals=allPeriodicals, msg_error=msg_error, lMonth=lMonth, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)
    return render_template('periodicalTwo.html', period=period, allPeriodicals=allPeriodicals, lMonth=lMonth, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)

@app.route('/mytrans', methods=['GET'])
@login_required
def mytransct():
    status, foundTrans = trans_list(current_user.user_id)
    return render_template('mytrans.html', status=status, foundTrans=foundTrans, allAuthors=allAuthors, currentYear=currentYear, allBooks=allBooks, allDepts=allDepts, allSubj=allSubj, allPubs=allPubs)

@app.route('/periodicals', methods=['GET','POST'])
@login_required
@admin_required
def periodicals():
    email = current_user.user_mail
    allSubj = Subject.query.all()
    if (request.method == "POST"):
        msg_success = ''
        status = add_period()
        if status:
            msg_success = "Periodical Added Successfully"
        else:
            msg_success = "AN Error Occurred"
        return render_template('periodicals.html', allPeriodicals=allPeriodicals, msg_success=msg_success, lMonth=lMonth, email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)
    return render_template('periodicals.html', allPeriodicals=allPeriodicals, lMonth=lMonth, email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)

@app.route('/periodicals/<id>', methods=['GET','POST'])
@login_required
@admin_required
def get_periodicals(id):
    email = current_user.user_mail
    allSubj = Subject.query.all()
    period = get_period(id)
    msg_error = ''
    msg_success = ''
    if period is None:
            msg_error = "Periodical Not Found"
            return render_template('periodicals.html', allPeriodicals=allPeriodicals, msg_error=msg_error, lMonth=lMonth, email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)
    if (request.method == "POST"):
        status, period = update_period(id)
        if status:
            msg_success = "Update Successful"
            return render_template('periodicalDetails.html', period=period, msg_error=msg_error, msg_success=msg_success, lMonth=lMonth, email=email, currentYear=currentYear)
        else:
            msg_error = "Periodical Not Found"
            return render_template('periodicals.html', allPeriodicals=allPeriodicals, msg_success=msg_success, lMonth=lMonth, email=email, allDepts=allDepts, currentYear=currentYear, allSubj=allSubj, allAuthors=allAuthors, allPubs=allPubs, allBooks=allBooks)

        return render_template('periodicalDetails.html', period=period, msg_error=msg_error, msg_success=msg_success, lMonth=lMonth, email=email, currentYear=currentYear)
    return render_template('periodicalDetails.html', period=period, msg_error=msg_error, msg_success=msg_success, lMonth=lMonth, email=email, currentYear=currentYear)

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
