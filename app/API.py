from flask import jsonify, request, redirect, url_for, render_template
from app import app
from app import login_manager
from app.model import *
from app.models.User import User
from app.models.Product import Product
from app.models.Cart import Cart
from app.models.Order import Order
import flask_login



@app.route('/',methods=["GET"])
def test():
    return jsonify({"status":"1"})

@app.route('/api/user',methods=["GET"])
def userInfoAPI():
    if(flask_login.current_user is not None) and (flask_login.current_user.is_authenticated):
        return jsonify(User.getInfo(flask_login.current_user.userID))
    else:
        return jsonify({"status":"Not authenticated"})

@app.route('/api/books/<int:page>',methods=["GET"])
def testBooks(page):
    return jsonify(Product.getAllProfuctsFilteredByRate(page,5))

@app.route('/api/books/tags',methods=["GET"])
def testBooksByTags():
    tags = request.args.get('tags',type=str)
    tagsArray = tags.split(',')
    if(len(tagsArray) == 0):
        return jsonify({'status':3,'message':'Empty array of tags(','data':[]})
    return jsonify(Product.getAllProductsFilteredByTags(tagsArray))

@app.route('/api/cart',methods=['GET'])
def testGetCartOfUser():
    if(flask_login.current_user is not None) and (flask_login.current_user.is_authenticated):
        return jsonify(Cart.getCartOfUser(flask_login.current_user.userID))
    else:
        return jsonify({'message':'No auth','status':120})

@app.route('/flasklogin/check',methods = ['GET'])
def checkFlaskLogin():
    if flask_login.current_user.is_authenticated:
        return jsonify({'status':1})
    else:
        return jsonify({'status':0})

@app.route('/flasklogin/login',methods=['GET'])
def loginUserAPI():
    email = request.args.get('email',type=str)
    password = request.args.get('password',type=str)
    
    userID = User.validateUserAndReturnUserID(email,password)
    if(userID != -1):
        flask_login.login_user(load_user(userID),remember=True)
        return jsonify({'status':1})
    else:
        return jsonify({'status':0})

@app.route('/flasklogin/register',methods=["GET"])
def registerUser():
    if flask_login.current_user.is_authenticated:
        return jsonify({'status':2,'message':"you already auth"})
    else:
        email = request.args.get('email')
        password = request.args.get('password')
        birthdate = request.args.get('birthdate')
        first_name = request.args.get('first_name')
        last_name= request.args.get('last_name')

        result = {}
        resultRegisterOperation = User.registerUser(email,password,last_name,first_name,birthdate)
        if(resultRegisterOperation["status"] == 1):
            return jsonify(resultRegisterOperation)
        flask_login.login_user(load_user(resultRegisterOperation["userID"]),remember=True)
        result['status'] = 0
        result['message'] = 'OK'
        return jsonify(result)

@app.route('/flasklogin/logout',methods = ["GET"])
@flask_login.login_required
def logoutUserAPI():
    flask_login.logout_user()
    return jsonify({'status':1})

@app.route('/flasklogin/email',methods = ['GET'])
@flask_login.login_required
def checkEmail():
    return jsonify({'email':flask_login.current_user.email})

@app.route('/api/tags')
def getAvailableTagsAPI():
    return jsonify(Product.getAvailableTags())

@app.route('/api/order/add',methods=['GET'])
def addNewOrder():
    if(flask_login.current_user.is_authenticated):
        
        return jsonify(Order.addNewOrder(flask_login.current_user.userID))
    else:
        return jsonify({'message':'Not auth','status':120})

@app.route('/api/cart/add',methods=['GET'])
def addItemsInCart():
    productID = request.args.get('product',type=int)
    if(flask_login.current_user.is_authenticated):
        return jsonify(Cart.addItemInCartOfUser(flask_login.current_user.userID,productID))
    else:
        return jsonify({'message':'Not auth','status':120})

@app.route('/api/cart/remove')
def removeItemInCart():
    productID = request.args.get('product',type=int)
    if(flask_login.current_user.is_authenticated):
        return jsonify(Cart.removeItemInCartOfUser(
            flask_login.current_user.userID,productID))
    else:
        return jsonify({'message':'Not auth','status':120})

@app.route('/api/rate',methods=['GET'])
def setRate():
    user = flask_login.current_user
    if(user.is_authenticated):
        productID = request.args.get('productID',type=int)
        mark = request.args.get('mark',type=int)
        result = Product.addNewRate(user.userID,productID,mark)
        return jsonify(result)
    return jsonify({'status':120,'message':'Not auth'})

@app.route('/api/books/detail/<int:productID>')
def showDetailsOfBookAPI(productID):
    return Product.getDetailsOfProduct(productID)