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
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user1 = User(
            username="testuser1",
            first_name="test1",
            last_name="user1",
            email="testuser1@email.com",
            password="HASHED_PASSWORD",
        )

        db.session.add(user1)
        db.session.commit()

        self.client = app.test_client()

        user3 = User.signup(
            username="testuser3",
            first_name="test3",
            last_name="user3",
            email="testuser3@email.com",
            password="HASHED_PASSWORD3",
        )

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        user2 = User(
            username="testuser2",
            first_name="test2",
            last_name="user2",
            email="testuser2@email.com",
            password="HASHED_PASSWORD2",
        )

        db.session.add(user2)
        db.session.commit()

        # User should have no pins record & no assets
        self.assertEqual(len(user2.pins), 0)
        self.assertEqual(len(user2.assets), 0)

    # SignUp Tests
    def test_valid_user_signup(self):
        """Test user method signup"""

        user2 = User.signup(
            username="testuser2",
            first_name="test2",
            last_name="user2",
            email="testuser2@email.com",
            password="HASHED_PASSWORD2",
        )

        self.assertNotEqual(user2.password, "HASHED_PASSWORD2")
        self.assertEqual(len(User.query.all()), 3)

    def test_invalid_username_signup(self):

        with self.assertRaises(exc.IntegrityError) as context:
            invalid_user = User.signup(
                username="testuser1",
                first_name="test1",
                last_name="user1",
                email="testuser1@email.com",
                password="HASHED_PASSWORD",
            )

    # Authentication tests

    def test_valid_authentication(self):
        user = User.authenticate("testuser3", "HASHED_PASSWORD3")
        self.assertIsNotNone(user)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("testuser2", "HASHED_PASSWORD"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate("testuser3", "incorrect"))
