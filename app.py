import os

from flask import Flask, request, jsonify
from datetime import datetime
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from models import db, connect_db, User, Asset, Coins, Pins
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS

app = Flask(__name__)

uri = os.environ.get("DATABASE_URL", "postgresql:///capstone_2")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_DATABASE_URI"] = uri

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "secret")
app.config["SQLALCHEMY_ECHO"] = True

# Setup the Flask-JWT-Extended extension. 
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", "secret")
jwt = JWTManager(app)
CORS(app)

connect_db(app)



###### signup/login/logout


@app.route("/auth/register", methods=["POST"])
def signup():
    """Sign up user."""
    try:
        user = User.signup(
            username = request.json.get('username', None),
            first_name = request.json.get('firstName', None),
            last_name = request.json.get('lastName', None),
            email = request.json.get('email', None),
            password = request.json.get('password', None)
            )

        token = create_access_token(identity={"username": user.username})

        return {"token": token}, 200

    except IntegrityError as e:
        if 'duplicate key value violates unique constraint "users_pkey"' in str(e.orig):
            return jsonify({'msg':'Username Already Exists'}), 400
        elif 'duplicate key value violates unique constraint "users_email_key"' in str(e.orig):
            return jsonify({'msg':'Email Already Exists'}), 400
        return jsonify({'msg':'Database Error'}), 400


@app.route("/auth/login", methods=["GET", "POST"])
def login():
    """Handle user login."""

    try:
        user = User.authenticate(request.json.get('username', None), request.json.get('password', None))
        token = create_access_token(identity={"username": user.username})
        return {"token": token}, 200
    
    except AttributeError:
        return jsonify({'msg':'Incorrect username or password'}), 400

# protected route
# @app.route('/protected', methods=['GET'])
# @jwt_required()
# def test():
#     user = get_jwt_identity()
#     username = user['username']
#     print(user)
#     return f'Welcome to the protected route {username}!', 200
 
@app.route('/users/<username>', methods=['GET'])
@jwt_required()
def get_current_user(username):
    dbUser =  User.get_user(username)
    print(dbUser.serialize())
    return jsonify({"user": dbUser.serialize()}), 200
  
 
@app.route('/users/<username>', methods=['PATCH'])
@jwt_required()
def update_current_user(username):

    first_name = request.json.get('firstName', None),
    last_name = request.json.get('lastName', None),
    email = request.json.get('email', None),
    user = User.update_user(username, first_name, last_name, email)
    print(user.serialize())
    return jsonify({"user": user.serialize()}), 201
  
@app.route('/users/pin/<coin_gecko_id>', methods=['POST'])
@jwt_required()
def pin_to_watchlist(coin_gecko_id):
    """Pin coin to logged in user's watchlist."""
    user = get_jwt_identity()
    username = user['username']
    db_coin = Coins.get_coin_by_coin_gecko_id(coin_gecko_id)
    pin = Pins.pin_coin_to_watchlist(username,db_coin.coin_id) 
    print(pin, "****************************************************************")
    return jsonify({"pin":pin.serialize()}), 200

@app.route('/users/unpin/<coin_gecko_id>', methods=['POST'])
@jwt_required()
def unpin_from_watchlist(coin_gecko_id):
    """Unpin coin from logged in user's watchlist."""
    user = get_jwt_identity()
    username = user['username']
    db_coin = Coins.get_coin_by_coin_gecko_id(coin_gecko_id)
    Pins.unpin_coin_from_watchlist(username,db_coin.coin_id)
    return username, 200

@app.route('/watchlist', methods=['GET'])
@jwt_required()
def get_user_watchlist():
    """Show list of coins this user is watching."""
    user = get_jwt_identity()
    username = user['username']
    pins = Pins.get_pins_by_user(username)
    return jsonify({"pins":Pins.serialize_list(pins)}), 200

@app.route('/coins/search', methods=['GET'])
@jwt_required()
def search_coins():
    "Search for coins in the coins table"
    search = request.args.get('search', None),
    coins = Coins.search_coins(search)
    coins_array=[Coins.serialize(coin) for coin in coins]
    return jsonify({"coins":coins_array})
    