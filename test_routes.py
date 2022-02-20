"""Views tests."""
# run these tests like:
#
# FLASK_ENV=production python -m unittest test_user_model.py
# (we set FLASK_ENV for this command, so it doesn’t use debug mode, and therefore won’t use the Debug Toolbar during our tests).

import os
from unittest import TestCase
from sqlalchemy import exc
from flask_jwt_extended import (
    JWTManager, create_access_token,
)
from models import db, User, Coins, Asset, Pins

os.environ["DATABASE_URL"] = "postgresql:///capstone_2_test"

from app import app
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///capstone_2_test"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
jwt = JWTManager(app)
# app.app_context().push()    

db.create_all()

class ViewsTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user1 = User.signup(
            username="testuser1",
            first_name="test1",
            last_name="user1",
            email="testuser1@email.com",
            password="HASHED_PASSWORD",
        )

        self.client = app.test_client()

        # user2 = User.signup(
        #     username="testuser2",
        #     first_name="test2",
        #     last_name="user2",
        #     email="testuser2@email.com",
        #     password="HASHED_PASSWORD2",
        # )

        coin = Coins(
            name="testcoin",
            symbol="TC",
            coin_gecko_id="testcoin",
        )

        db.session.add_all([coin])
        db.session.commit()

        user1_asset = Asset(username="testuser1", coin_id="testcoin", quantity="1")

        user1_pin = Pins(
            username="testuser1",
            coin_id="testcoin",
        )

        db.session.add_all([user1_asset, user1_pin])

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_list_user_watchlist_unauthorized(self):
        with self.client as c:
            resp = c.get("/watchlist")
            self.assertEqual(resp.status_code, 401)

