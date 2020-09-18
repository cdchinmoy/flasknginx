from flask import Blueprint, Flask, request, make_response, jsonify
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from project import db
import jwt
import datetime
from functools import wraps
from project.models import User, Seller, Product

user_bp = Blueprint('user_bp', __name__)

def user_token_required(f):
    @wraps(f)
    def user_decorated(*args, **kwargs):
        token = None
        if request.args.get('token'):
            token = request.args.get('token')

        if not token:
            return jsonify({'message' : 'Token is missing!'}, 401)

        try: 
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['id']).first()
            
        except:
            return jsonify({'message' : 'Token is invalid!'}, 401)

        return f(current_user, *args, **kwargs)

    return user_decorated             


@user_bp.route('/register', methods=['POST'])
def create_user():
    data = request.get_json()
    email_exist = User.check_email_exist(data['email'])
    if email_exist:
        return jsonify({'message':'There is already an account with this email id!'}, 201)
    username_exist = User.check_username_exist(data['username'])
    if username_exist:
        return jsonify({'message':'There is already an account with this username!'}, 201)
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(name=data['name'], email=data['email'], username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message':'New user created'}, 200)


@user_bp.route('/login', methods=['POST'])
def user_login():
    data = request.get_json()
    if not data and not data['username'] and not data['password']:
        return make_response('Could not verify', 401, {'WWW-Authenticate':'Login required'})
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate':'Login required'})

    if check_password_hash(user.password, data['password']):
        token = jwt.encode({'id' : user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=300)}, current_app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')}, 200) 
    
    return jsonify({'message': 'Invaild email or password'}, 201) 


@user_bp.route('/all', methods=['GET'])
@user_token_required
def get_all_users(current_user):
    if not current_user:
        return jsonify({'message' : 'Invaild Authorization Request!'}, 401)

    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.name
        user_data['email'] = user.email
        user_data['password'] = user.password
        output.append(user_data)

    return jsonify({'users': output}, 200) 


@user_bp.route('/products', methods=['GET'])
@user_token_required
def get_all_products(current_user):
    if not current_user:
        return jsonify({'message' : 'Invaild Authorization Request!'}, 401)

    products = Product.query.all()
    output = []
    product_data = {}
    for product in products:
        if product.sellers:
            product_data = {}
            product_data['id'] = product.id
            product_data['product_name'] = product.product_name
            product_data['product_price'] = product.product_price
            product_data['product_desc'] = product.product_desc
            
            if product.sellers:
                for seller_data in product.sellers:
                    product_data['seller_name'] = seller_data.name

            output.append(product_data)

    return jsonify({'products': output}, 200) 
        
