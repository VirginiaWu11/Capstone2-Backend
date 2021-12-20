from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    """User Model"""

    __tablename__ = "users"
    username = db.Column(db.Text, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)

    def serialize(self):
        """Returns a dictionary representation of user to turn into JSON"""
        return {
            "username": self.username,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
        }
    
    @classmethod
    def signup(
        cls,
        username,
        first_name,
        last_name,
        email,
        password,
    ):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    @classmethod
    def get_user(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def update_user(cls, username, first_name, last_name, email):
        user = cls.query.filter_by(username=username).first()
        print("******************",first_name, last_name, email)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        db.session.commit()
        return user
    
class Asset(db.Model):
    """Asset Model"""

    __tablename__ = "assets"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(
        db.Text,
        db.ForeignKey("users.username", ondelete="CASCADE"),
        nullable=False,
    )
    coin_id = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    def serialize(self):
        """Returns a dictionary representation of Asset to turn into JSON"""
        return {
            "username": self.username,
            "quantity": self.quantity,
        }

    def __repr__(self):
        return f"<Transaction id={self.id} username={self.username} quantity={self.quantity}>"
