import os

from flask import Flask, request, jsonify
from datetime import datetime
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from models import db, connect_db, User, Asset
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
            return jsonify({'error':{'message':'Username Already Exists'}}), 400
        elif 'duplicate key value violates unique constraint "users_email_key"' in str(e.orig):
            return jsonify({'error':{'message':'Email Already Exists'}}), 400
        return jsonify({'error':{'message':'Database Error'}}), 400


@app.route("/auth/login", methods=["GET", "POST"])
def login():
    """Handle user login."""

    try:
        user = User.authenticate(request.json.get('username', None), request.json.get('password', None))
        token = create_access_token(identity={"username": user.username})
        return {"token": token}, 200
    
    except AttributeError:
        return jsonify({'error':{'message':'Incorrect username or password'}}), 400

# protected route
@app.route('/protected', methods=['GET'])
@jwt_required()
def test():
    user = get_jwt_identity()
    username = user['username']
    print(user)
    return f'Welcome to the protected route {username}!', 200
 
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
  
 
