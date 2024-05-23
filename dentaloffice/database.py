import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")

products_db = myclient["products"]
branches = products_db["branches"]
order_management_db = myclient["order_management"]

def get_users():
    user_list = []
    customers_coll = order_management_db['customers']
    for c in customers_coll.find({}):
        user_list.append(c)

    return user_list

def get_user(username):
    customers_coll = order_management_db['customers']
    user=customers_coll.find_one({"username":username})
    return user

def change_password(username, password):
    customers_coll = order_management_db['customers']
    customers_coll.update_one({"username":username}, {"$set":{"password":password}})
    temp = get_user(username)
    user={"username":username,
                  "first_name":temp["first_name"],
                  "last_name":temp["last_name"]}
    return user

def get_product(code):
    products_coll = products_db["products"]
    product = products_coll.find_one({"code":code},{"_id":0})

    return product


def get_products():
    product_list = []

    products_coll = products_db["products"]

    for p in products_coll.find({},{"_id":0}):
        product_list.append(p)

    return product_list

def get_branch(code):
    branch = branches.find_one({"code":str(code)})
    return branch

def get_branches():
    return list(branches.find())

def create_order(order):
    orders_coll = order_management_db['orders']
    orders_coll.insert_one(order)

def get_orders(user):
    order_list = []
    orders_coll = order_management_db['orders']
    for o in orders_coll.find({"username":user}):
        order_list.append(o)

    return order_list