"""User model tests."""
# run these tests like:
#
# FLASK_ENV=production python -m unittest test_user_model.py
# (we set FLASK_ENV for this command, so it doesn’t use debug mode, and therefore won’t use the Debug Toolbar during our tests).

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User

os.environ["DATABASE_URL"] = "postgresql:///capstone_2_test"

from app import app

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///capstone_2_test"

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User(
            username="testuser1",
            first_name="test1",
            last_name="user1",
            email="testuser1@email.com",
            password="HASHED_PASSWORD",
        )

        db.session.add(u1)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u2 = User(
            username="testuser2",
            first_name="test2",
            last_name="user2",
            email="testuser2@email.com",
            password="HASHED_PASSWORD2",
        )

        db.session.add(u2)
        db.session.commit()

        # User should have no pins record & no assets
        self.assertEqual(len(u2.pins), 0)
        self.assertEqual(len(u2.assets), 0)

    # SignUp Tests
    def test_valid_user_signup(self):
        """Test user method signup"""

        u2 = User.signup(
            username="testuser2",
            first_name="test2",
            last_name="user2",
            email="testuser2@email.com",
            password="HASHED_PASSWORD2",
        )

        self.assertNotEqual(u2.password, "HASHED_PASSWORD2")
        self.assertEqual(len(User.query.all()), 2)
