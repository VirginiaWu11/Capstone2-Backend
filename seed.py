from app import app
from models import db, User, Asset, Pins, Coins
from csv import DictReader

db.drop_all()
db.create_all()

user1 = User(
    username="testuser1",
    first_name="test",
    last_name="user",
    email="test@user.com",
    password="$2b$12$Ohf7Ash2AICMJDHRPn7oquzJrOkdgBxjRvFhvJqcVKR7UyCtt7lwC",
)
# password is: testuser

# asset1 = Asset(
#     username="testuser1",
#     quantity=500,
#     coin_id="bitcoin",
# )

pin1 = Pins(
    username="testuser1",
    coin_id=1498,
)
pin2 = Pins(
    username="testuser1",
    coin_id=1499,
)
pin3 = Pins(
    username="testuser1",
    coin_id=300,
)
pin4 = Pins(
    username="testuser1",
    coin_id=200,
)
pin5 = Pins(
    username="testuser1",
    coin_id=100,
)

"""Seed database from coins.csv file."""

with open("generator/coins.csv") as coins:
    db.session.bulk_insert_mappings(Coins, DictReader(coins))

db.session.add_all(
    [
        user1,
    ]
)
db.session.commit()


db.session.add_all(
    [
        pin1,pin2,pin3,pin4,pin5
    ]
)

db.session.commit()
