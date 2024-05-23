from flask import Flask,redirect
from flask import render_template, request, session, flash
from bson.json_util import loads, dumps
from flask import make_response
import database as db
import ordermanagement as om
import authentication
import logging


app = Flask(__name__)

# Set the secret key to some random bytes. 
# Keep this really secret!
app.secret_key = 's@g@d@c0ff33!'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(int(code))

    return render_template('branchdetails.html', branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods = ['GET', 'POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    fmessage = 'Invalid username or password. Please try again.'

    if username=='' or password=='':
        flash(fmessage)
        return redirect('/login')
    
    try:
        test = db.get_user(username)
    except:
        flash(fmessage)
        return redirect('/login')
    
    if test["password"] != password:
        flash(fmessage)
        return redirect('/login')

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')

@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    if(session.get("cart") is None):
        session["cart"]={}
    elif(code in session["cart"]):
        cart=session["cart"]
        price=(cart[code]["subtotal"])/cart[code]["qty"]
        cart[code]["qty"] += 1
        cart[code]["subtotal"] =  cart[code]["qty"] * price
        session["cart"]=cart
        return redirect('/cart')
    item=dict()
    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = product["price"]*item["qty"]
    item["price"] = product["price"]

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/updatecart', methods = ['POST'])
def updatecart():
    qty = request.form.getlist("qty")
    prices = request.form.getlist("prices")
    cart = session["cart"]
    i = 0
    for key in cart:
        cart[key]["qty"] = int(qty[i])
        cart[key]["subtotal"] = int(qty[i]) * float(prices[i])
        i+=1
    session["cart"]=cart
    return redirect('/cart')

@app.route('/removefcart')
def removefcart():
    name = request.args.get('name', '')
    product_list = db.get_products()
    for i in product_list:
        if i["name"] == name:
            code = i["code"]
            break
    cart = session["cart"]
    if len(cart)==1:
        session.pop("cart",None)
        return redirect('/cart')
    else:
        cart.pop(str(code))
        session["cart"]=cart
        return redirect('/cart')
    
@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/orders')
def orders():
    order_list = db.get_orders(session["user"]["username"])
    return render_template('orders.html', page="Orders", order_list=order_list)

@app.route('/changepass', methods = ['GET', 'POST'])
def changepass():
    return render_template('changepassword.html')
    
@app.route('/checkpass', methods = ['GET', 'POST'])
def checkpass():
    oldpass = request.form.get('oldpass')
    newpass = request.form.get('newpass')
    username = session["user"]["username"]
    cpass = request.form.get('cpass')
    user = db.get_user(session["user"]["username"])

    if oldpass=="" or newpass=="" or cpass=="":
        flash('Please fill in all the fields.')
        return redirect('/changepass')
    
    if oldpass!=user["password"]:
        flash('Please enter your old password.')
        return redirect('/changepass')
    
    if newpass==oldpass:
        flash('New password cannot be your old password.')
        return redirect('/changepass')
    
    if newpass!=cpass:
        flash('Plase confirm new password.')
        return redirect('changepass')
    
    user = db.change_password(username, newpass)
    session["user"]= user
    flash('Password changed successfully.')
    return redirect('/changepass')

@app.route('/api/products',methods=['GET'])
def api_get_products():
    resp = make_response( dumps(db.get_products()) )
    resp.mimetype = 'application/json'
    return resp

@app.route('/api/products/<int:code>',methods=['GET'])
def api_get_product(code):
    resp = make_response(dumps(db.get_product(code)))
    resp.mimetype = 'application/json'
    return resp

    