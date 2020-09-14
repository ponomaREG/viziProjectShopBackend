from flask import jsonify, request, redirect, url_for, render_template
from app import app
from app import login_manager
from app.model import *
from app.models.User import User
from app.models.Product import Product
from app.models.Cart import Cart
from app.models.Order import Order
from utils import pageHelper
import flask_login


    
    
@app.route("/",method=['GET'])
def main():
    return redirect(url_for('showBooks',page=1))

@app.route("/login",methods = ['GET','POST'])
def loginUser():
    if(flask_login.current_user.is_authenticated):
        return redirect(url_for('userInfo'))
    if(request.method == 'POST'):
        email = request.form.get('email',type=str)
        password = request.form.get('password',type=str)
        userID = User.validateUserAndReturnUserID(email,password)
        if(userID != -1):
            flask_login.login_user(load_user(userID),remember=True)
            return redirect(url_for('showBooks',page=1))
        else:
            return render_template('login.html',error = "Not found")
    else:
        return render_template('login.html')

@app.route('/registration',methods=['GET','POST'])
def registrationUser():
    if(flask_login.current_user.is_authenticated):
        return redirect(url_for('userInfo'))
    if(request.method == 'POST'):
        email = request.form.get('email',type=str)
        pswd = request.form.get('pswd',type=str)
        pswd2 = request.form.get('pswd2',type=str)
        first_name = request.form.get('firstName',type=str)
        last_name = request.form.get('lastName',type=str)
        birthdate = request.form.get('birthDate')
        if(pswd != pswd2):
            return render_template('registration.html',error = 'Password mismatch')
        resultRegisterOperation = User.registerUser(email,pswd,last_name,first_name,birthdate)
        if(resultRegisterOperation["status"] == 1):
            return render_template('registration.html',error = 'User already exists')
        flask_login.login_user(load_user(resultRegisterOperation["userID"]),remember=True)
        return redirect(url_for('userInfo'))
    else:
        return render_template('registration.html')


@app.route('/user',methods=['GET'])
@flask_login.login_required
def userInfo():
    return render_template('check.html',user = flask_login.current_user)

@app.route('/logout',methods=['GET'])
@flask_login.login_required
def logoutUser():
    flask_login.logout_user()
    return redirect(url_for('loginUser'))

@app.route('/books/<int:page>',methods=["GET"])
def showBooks(page):
    if(page < 1):
        return render_template('books.html',error = 'Incorrect page',user = flask_login.current_user)
    OFFSET = 12
    userQuerySearch = request.args.get('q',default=None,type=str)
    if(userQuerySearch is None):
        result = Product.getAllProfuctsFilteredByRate(page,OFFSET)
    else:
        result = Product.getAllProfuctsFilteredByQuery(userQuerySearch,page,OFFSET)
    if(result['status'] == 0):
        countOfRows = Product.getQuantityOfRowsInTable()['count']
        countOfPages = countOfRows // OFFSET
        if(countOfRows % OFFSET > 0):
            countOfPages += 1
        countOfPagesRange = pageHelper.getRangeOfPages(countOfPages,page)
        return render_template(
            'books.html', #TODO : IF STATUS
            products = result['data'],
            countOfPagesRange = countOfPagesRange,
            user = flask_login.current_user,
            q = userQuerySearch,
            currentPage=page)
    elif(result['status'] == 2):
        return render_template('books.html',
        error = 'Empty data',
        user = flask_login.current_user,
        q = userQuerySearch)
    elif(result['status'] == 1):
        return render_template('books.html',
        error = 'SQL runtime error',
        user = flask_login.current_user)
    return render_template('books.html',error='ERROR',user = flask_login.current_user)


@app.route('/books/details/<int:productID>')
def showDetailsOfBook(productID):
    details = Product.getDetailsOfProduct(productID)
    print(details)
    if(details['status'] == 0):
        return render_template('shop-details.html',
        user = flask_login.current_user,details = details['data'][0])
    elif(details['status'] == 2):
        return render_template('shop-details.html',
        user = flask_login.current_user,error = details['message'])
    elif(details['status'] == 1): #TODO: ERROR
        return render_template('shop-details.html',
        user = flask_login.current_user,error = details['message'])
    else:
        return redirect(url_for('showBooks',page=1))
