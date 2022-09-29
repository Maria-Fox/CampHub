"""User model tests."""

# To run tests: python3 -m unittest tests/models/test_user_model.py

from unittest import TestCase
from models import db, User
import os 

os.environ['DATABASE_URL'] = "postgresql:///camphub_test"

from app import app 
db.create_all()

class UserModelTestCase(TestCase):
    '''Test user model to include registering a user and logining in/ authenticating. '''

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.register(
            username= "user1",
            password = "password1",
            school_name = "Springboard",
            field_of_study = "Software Engineering"
        )

        u1.id = 888

        u2 = User.register(username= "user2",
            password = "password2",
            school_name = "Springboard",
            field_of_study = "UX Design"
        )

        u2.id = 999

        db.session.commit()
        # u1 = User.query.get(u1.id)
        # u2 = User.query.get(u2.id)

        self.u1= u1
        self.u2= u2

        self.client = app.test_client()

    def tearDown(self):
        """Clean up transactions."""
        db.session.rollback()

    #      #      #      #      #      #      #      #      #      #  

    def test_user_model(self):
        '''Test creating a user instance - no methods.'''

        test_user_model = User( 
            username = "test_user456", 
            password = "password_test", 
            school_name = "Springboard", 
            field_of_study = "Software Dev")

        db.session.add(test_user_model)
        db.session.commit()

        self.assertEqual(test_user_model.username, "test_user456")
        self.assertEqual(test_user_model.school_name, "Springboard")
        self.assertEqual(test_user_model.field_of_study, "Software Dev")


    #      #      #      #      #      #      #      #      #      

    def test_user_register(self):
        '''Test creating a user instance using the class register method.'''

        test_user_register = User.register( 
            username = "test_user789", 
            password = "password_test", 
            school_name = "Springboard", 
            field_of_study = "Software Dev")

        test_user_register.id = 789

        db.session.add(test_user_register)
        db.session.commit()

        testing_user = User.query.get(789)

        self.assertIsInstance(testing_user, User)
        self.assertEqual(testing_user.username, "test_user789")
        self.assertEqual(testing_user.school_name, "Springboard")
        self.assertEqual(testing_user.field_of_study, "Software Dev")

    #      #      #      #      #      #      #      #      #      


    def test_user_authentication(self):
        '''Test using User class method authentication'''

        user = User.authenticate(self.u1.username, "password1")

        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.u1.id)

    #      #      #      #      #      #      #      #      #      


    def test_invalid_user(self):
        '''Test incorrect user credentials do not authenticate a user.'''

        attempt_1 = User.authenticate("user1", "wrong_password")
        attempt_2 = User.authenticate("wrong_user", "password2")

        self.assertFalse(attempt_1)
        self.assertFalse(attempt_2)
