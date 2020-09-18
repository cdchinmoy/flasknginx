from flask import Flask, request, make_response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from db import db
import jwt
import datetime
from functools import wraps
from models import User, Seller, Product

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

def user_token_required(f):
    @wraps(f)
    def user_decorated(*args, **kwargs):
        token = None
        if request.args.get('token'):
            token = request.args.get('token')

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['id']).first()
            
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return user_decorated             

def seller_token_required(f):
    @wraps(f)
    def seller_decorated(*args, **kwargs):
        token = None
        if request.args.get('token'):
            token = request.args.get('token')

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_seller = Seller.query.filter_by(id=data['id']).first()
            
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_seller, *args, **kwargs)

    return seller_decorated



@app.route('/seller/register', methods=['POST'])
def create_seller():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_seller = Seller(id=str(uuid.uuid4()), name=data['name'], email=data['email'], username=data['username'], password=hashed_password)
    db.session.add(new_seller)
    db.session.commit()
    return jsonify({'message':'New seller created'})

@app.route('/seller/login', methods=['POST'])
def seller_login():
    data = request.get_json()
    if not data and not data['username'] and not data['password']:
        return make_response('Could not verify', 401, {'WWW-Authenticate':'Login required'})
    seller = Seller.query.filter_by(username=data['username']).first()
    if not seller:
        return make_response('Could not verify', 401, {'WWW-Authenticate':'Login required'})

    if check_password_hash(seller.password, data['password']):
        token = jwt.encode({'id' : seller.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=300)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')}) 
    
    return jsonify({'message': 'Invaild email or password'}) 


@app.route('/user/register', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(id=str(uuid.uuid4()), name=data['name'], email=data['email'], username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message':'New user created'})


@app.route('/users', methods=['GET'])
@user_token_required
def get_all_users(current_user):
    if not current_user:
        return jsonify({'message' : 'Cannot perform that function!'})

    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.name
        user_data['email'] = user.email
        user_data['password'] = user.password
        output.append(user_data)

    return jsonify({'users': output}) 

'''
@app.route('/user/products', methods=['GET'])
@user_token_required
def get_all_seller_product(current_seller):
    if not current_seller:
        return jsonify({'message' : 'Cannot perform that function!'})

    #products = db.session.query(Product.product_name,Product.product_price,Seller.name).join(Seller_product, Product.id==Seller_product.product_id).join(Seller, Seller_product.seller_id==Seller.id).all()
    products = Product.query.all()
    output = []
    for pro in products.seller:
        #print(product)
        product_data = {}
        #product_data['product_name'] = product.product_name
        #product_data['product_price'] = product.product_price
        product_data['seller_name'] = pro.name
        output.append(product_data)

    return jsonify({'products': output})  
'''

@app.route('/sellers', methods=['GET'])
@seller_token_required
def get_all_sellers(current_seller):
    if not current_seller:
        return jsonify({'message' : 'Cannot perform that function!'})

    sellers = Seller.query.all()
    output = []
    for seller in sellers:
        seller_data = {}
        seller_data['id'] = seller.id
        seller_data['name'] = seller.name
        seller_data['email'] = seller.email
        seller_data['password'] = seller.password
        output.append(seller_data)

    return jsonify({'sellers': output})     

@app.route('/seller/product', methods=['POST'])
@seller_token_required
def create_product(current_seller):
    if not current_seller:
        return jsonify({'message' : 'Cannot perform that function!'})

    data = request.get_json()
    new_product = Product(product_name=data['product_name'], product_price=data['product_price'], product_desc=data['product_desc'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message':'New product created'})


@app.route('/seller/products', methods=['GET'])
@seller_token_required
def get_all_product(current_seller):
    if not current_seller:
        return jsonify({'message' : 'Cannot perform that function!'})

    products = Product.query.all()
    output = []
    for product in products:
        product_data = {}
        product_data['id'] = product.id
        product_data['product_name'] = product.product_name
        product_data['product_price'] = product.product_price
        product_data['product_desc'] = product.product_desc
        output.append(product_data)

    return jsonify({'products': output})  

'''
@app.route('/seller/product/map', methods=['POST'])
@seller_token_required
def map_product(current_seller):
    if not current_seller:
        return jsonify({'message' : 'Cannot perform that function!'})

    data = request.get_json()

    product_data = Product.query.filter_by(id=data['product_id']).first()
    if not product_data:
        return jsonify({'message' : 'Product does not exist!'})

    seller_data = Seller.query.filter_by(id=current_seller.id).first()
    if not seller_data:
        return jsonify({'message' : 'Seller does not exist!'})

    seller_product_data = Seller_product.query.filter_by(product_id=data['product_id']).first()
    if seller_product_data:
        print(seller_data)
    else:
        map_product = Seller_product(product_id=data['product_id'], seller_id=current_seller.id)
        db.session.add(map_product)
        db.session.commit()
    return jsonify({'message':'Product has been mapped with seller'})  
'''

'''
@app.route('/seller/product/mapped_product', methods=['GET'])
@seller_token_required
def mapped_product(current_seller):
    if not current_seller:
        return jsonify({'message' : 'Cannot perform that function!'})

    mapped_data = Seller_product.query.filter_by(seller_id=current_seller.id).all()
    print(mapped_data)
    if mapped_data:
        output = []
        for data in mapped_data:
            list_data = {}
            list_data['id'] = data.id
            list_data['seller_id'] = data.seller_id
            list_data['product_id'] = data.product_id
            output.append(list_data)
        return jsonify({'seller_product': output})   
    else:
        return jsonify({'message': "No product mapped with this seller"})
'''

'''
@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    print(auth)
    if not auth and not auth.username and not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate':'Login required'})
    user = User.query.filter_by(username=auth.username).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate':'Login required'})

    if check_password_hash(user.password, auth.password):
        return jsonify({'message': 'Login successful'})   
    
    return jsonify({'message': 'Invaild email or password'})  
'''

@app.route('/user/login', methods=['POST'])
def user_login():
    data = request.get_json()
    if not data and not data['username'] and not data['password']:
        return make_response('Could not verify', 401, {'WWW-Authenticate':'Login required'})
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate':'Login required'})

    if check_password_hash(user.password, data['password']):
        token = jwt.encode({'id' : user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=300)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')}) 
    
    return jsonify({'message': 'Invaild email or password'}) 



if __name__ == "__main__":
    app.run(debug=True)