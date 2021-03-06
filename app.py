import os

from flask import Flask, request, jsonify
from datetime import datetime
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
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
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "secret")
jwt = JWTManager(app)
CORS(app)

connect_db(app)

###### signup/login/logout


@app.route("/auth/register", methods=["POST"])
def signup():
    """Sign up user."""
    try:
        username = User.signup(
            username=request.json.get("username", None),
            first_name=request.json.get("firstName", None),
            last_name=request.json.get("lastName", None),
            email=request.json.get("email", None),
            password=request.json.get("password", None),
        )

        token = create_access_token(identity={"username": username})

        return {"token": token}, 200

    except Exception as e:
        print("*****e",e)
        return jsonify({"msg": f"{e}"}), 400

@app.route("/auth/login", methods=["GET", "POST"])
def login():
    """Handle user login."""

    try:
        username = User.authenticate(
            request.json.get("username", None), request.json.get("password", None)
        )
        token = create_access_token(identity={"username": username})
        return {"token": token}, 200

    except AttributeError:
        return jsonify({"msg": "Incorrect username or password"}), 400

@app.route("/users/<username>", methods=["GET"])
@jwt_required()
def get_current_user(username):
    dbUser = User.get_user(username)
    return jsonify({"user": dbUser.serialize()}), 200


@app.route("/users/<username>", methods=["PATCH"])
@jwt_required()
def update_current_user(username):

    first_name = (request.json.get("firstName", None),)
    last_name = (request.json.get("lastName", None),)
    email = (request.json.get("email", None),)
    user = User.update_user(username, first_name, last_name, email)
    return jsonify({"user": user.serialize()}), 201


@app.route("/users/pin/<coin_gecko_id>", methods=["POST"])
@jwt_required()
def pin_to_watchlist(coin_gecko_id):
    """Pin coin to logged in user's watchlist."""
    user = get_jwt_identity()
    username = user["username"]
    db_coin = Coins.get_coin_by_coin_gecko_id(coin_gecko_id)
    pin = Pins.pin_coin_to_watchlist(username, db_coin.coin_id)
    return jsonify({"pin": pin.serialize()}), 200


@app.route("/users/unpin/<coin_gecko_id>", methods=["POST"])
@jwt_required()
def unpin_from_watchlist(coin_gecko_id):
    """Unpin coin from logged in user's watchlist."""
    user = get_jwt_identity()
    username = user["username"]
    db_coin = Coins.get_coin_by_coin_gecko_id(coin_gecko_id)
    Pins.unpin_coin_from_watchlist(username, db_coin.coin_id)
    return username, 200


@app.route("/watchlist", methods=["GET"])
@jwt_required()
def get_user_watchlist():
    """Show list of coins this user is watching."""
    user = get_jwt_identity()
    username = user["username"]
    pins = Pins.get_pins_by_user(username)
    return jsonify({"pins": Pins.serialize_list(pins)}), 200


@app.route("/users/addasset/<coin_gecko_id>/<quantity>", methods=["POST"])
@jwt_required()
def add_to_portfolio(coin_gecko_id, quantity):
    """Add coin to logged in user's portfolio."""
    user = get_jwt_identity()
    username = user["username"]
    db_coin = Coins.get_coin_by_coin_gecko_id(coin_gecko_id)
    asset = Asset.add_coin_to_portfolio(username, db_coin.coin_id, quantity)
    return jsonify({"asset": asset.serialize()}), 200


@app.route("/users/removeasset/<coin_gecko_id>", methods=["POST"])
@jwt_required()
def remove_from_portfolio(coin_gecko_id):
    """Remove coin from logged in user's portfolio."""
    user = get_jwt_identity()
    username = user["username"]
    db_coin = Coins.get_coin_by_coin_gecko_id(coin_gecko_id)
    Asset.remove_coin_from_portfolio(username, db_coin.coin_id)
    return username, 200


@app.route("/portfolio", methods=["GET"])
@jwt_required()
def get_user_portfolio():
    """Show list of assets user's assets."""
    user = get_jwt_identity()
    username = user["username"]
    assets = Asset.get_assets_by_user(username)
    return jsonify({"assets": Asset.serialize_list(assets)}), 200


@app.route("/coins/search", methods=["GET"])
@jwt_required()
def search_coins():
    "Search for coins in the coins table"
    search = (request.args.get("search", None),)
    coins = Coins.search_coins(search)
    coins_array = [Coins.serialize(coin) for coin in coins]
    return jsonify({"coins": coins_array})
