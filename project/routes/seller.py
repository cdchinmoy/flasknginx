from flask import Blueprint, Flask, request, make_response, jsonify
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from project import db
import jwt
import datetime
from functools import wraps
from project.models import Seller, Product

seller_bp = Blueprint('seller_bp', __name__)

def seller_token_required(f):
    @wraps(f)
    def seller_decorated(*args, **kwargs):
        token = None
        if request.args.get('token'):
            token = request.args.get('token')

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        try: 
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            current_seller = Seller.query.filter_by(id=data['id']).first()
            
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_seller, *args, **kwargs)

    return seller_decorated


@seller_bp.route('/register', methods=['POST'])
def create_seller():

    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    email_exist = Seller.check_email_exist(data['email'])
    if email_exist:
        return jsonify({'message':'There is already an account with this email id!'})
    username_exist = Seller.check_username_exist(data['username'])
    if username_exist:
        return jsonify({'message':'There is already an account with this username!'})
    new_seller = Seller(name=data['name'], email=data['email'], username=data['username'], password=hashed_password)
    
    db.session.add(new_seller)
    db.session.commit()
    return jsonify({'message':'New seller created'})

@seller_bp.route('/login', methods=['POST'])
def seller_login():
    data = request.get_json()
    if not data and not data['username'] and not data['password']:
        return make_response('Could not verify', 401, {'WWW-Authenticate':'Login required'})
    seller = Seller.query.filter_by(username=data['username']).first()
    if not seller:
        return make_response('Could not verify', 401, {'WWW-Authenticate':'Login required'})

    if check_password_hash(seller.password, data['password']):
        token = jwt.encode({'id' : seller.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=300)}, current_app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')}) 
    
    return jsonify({'message': 'Invaild email or password'}) 


@seller_bp.route('/all', methods=['GET'])
@seller_token_required
def get_all_sellers(current_seller):
    if not current_seller:
        return jsonify({'message' : 'Invaild Authorization Request!'})

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


@seller_bp.route('/product/add', methods=['POST'])
@seller_token_required
def create_product(current_seller):
    if not current_seller:
        return jsonify({'message' : 'Invaild Authorization Request!'})

    data = request.get_json()
    new_product = Product(product_name=data['product_name'], product_price=data['product_price'], product_desc=data['product_desc'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message':'New product created'})


@seller_bp.route('/product/map', methods=['POST'])
@seller_token_required
def product_mapping(current_seller):
    if not current_seller:
        return jsonify({'message' : 'Invaild Authorization Request!'})

    data = request.get_json()
    product_id = data['product_id']
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return jsonify({'message' : 'Product does not exist!'})
    seller = current_seller
    product.sellers = [seller]

    db.session.add(product)
    db.session.commit()
    return jsonify({'message':'Product mapped with seller!'})
