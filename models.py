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
    email = db.Column(db.Text, unique=True, nullable=False)
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
    coin_id = db.Column(
        db.Integer, db.ForeignKey("coins.coin_id", ondelete="CASCADE"), nullable=False
    )
    quantity = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref='assets')
    coin = db.relationship('Coins', backref='assets')

    def serialize(self):
        """Returns a dictionary representation of Asset to turn into JSON"""
        return {
            "username": self.username,
            "quantity": self.quantity,
            "coin_id": self.coin_id,
        }

    def __repr__(self):
        return f"<Transaction id={self.id} username={self.username} quantity={self.quantity}>"


class Pins(db.Model):
    """Pins Model"""

    __tablename__ = "pins"

    username = db.Column(
        db.Text,
        db.ForeignKey("users.username", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    coin_id = db.Column(
        db.Integer, db.ForeignKey("coins.coin_id", ondelete="CASCADE"),primary_key=True, nullable=False
    )
    user = db.relationship('User', backref='pins')
    coin = db.relationship('Coins', backref='pins')

    def serialize(self):
        """Returns a dictionary representation of pins to turn into JSON"""
        # return {
        #     "username": self.username,
        #     "coin_id": self.coin_id,
        #     "coin_gecko_id":self.coin.coin_gecko_id,
        # }
        return self.coin.coin_gecko_id

    
    def __repr__(self):
        return f"<Transaction username={self.username} coin_id={self.coin_id}>"

    @classmethod
    def serialize_list(cls,list):
        return [item.serialize() for item in list]
            
    @classmethod
    def get_pins_by_user(cls, username):
        return cls.query.filter_by(username=username).all()

    @classmethod
    def pin_coin_to_watchlist(cls, username, coin_id):
        pin = Pins(username = username, coin_id = coin_id)
        db.session.add(pin)
        db.session.commit()
        return pin

    @classmethod
    def unpin_coin_from_watchlist(cls, username, coin_id):
        pin = cls.query.filter_by(username=username, coin_id=coin_id).first()
        db.session.delete(pin)
        db.session.commit()
        return pin


class Coins(db.Model):
    """Coins Model"""

    __tablename__ = "coins"
    coin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    symbol = db.Column(db.Text, nullable=False)
    coin_gecko_id = db.Column(db.Text, nullable=False)

    def serialize(self):
        """Returns a dictionary representation of coins to turn into JSON"""
        return {
            "coinId": self.coin_id,
            "name": self.name,
            "symbol": self.symbol,
            "coinGeckoId": self.coin_gecko_id,
        }

    def __repr__(self):
        return f"<Transaction id={self.coin_id} name={self.name} symbol={self.symbol} coin_id={self.coin_id}>"

    @classmethod
    def get_coin_by_coin_gecko_id(cls, coin_gecko_id):
        return cls.query.filter_by(coin_gecko_id=coin_gecko_id).first()

    @classmethod
    def get_coin_by_coin_id(cls, coin_id):
        return cls.query.filter_by(coin_id=coin_id).first()

    @classmethod
    def search_coins(cls, search):
        search = "%{}%".format("".join(search))
        return cls.query.filter(cls.name.ilike(search)).all()

