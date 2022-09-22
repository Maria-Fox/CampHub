"""User model tests."""

# To run tests: python3 -m unittest tests/models/test_user_model.py

from unittest import TestCase
from models import db, User
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres:///camphub_test"

from app import app 
db.create_all()

class UserModelTestCase(TestCase):
    '''Test user model to include registering a user and logining in/ authenticating. '''

    def set_up(self):
      '''Create test client and test user.'''

      db.drop_all()
      db.create_all()

      user1 = User.register("testUser1", "password1", "Springboard", "Software Engineering")
      user2 = User.register("user2", "password2", "Springboard", "UX Design")

      user1.id = 888
      user2.id = 999

      db.session.add_all([user1, user2])
      db.session.commit()

      self.client = app.client()

    def tear_down(self):
      db.session.rollback()

    #      #      #      #      #      #      #      #      #      #  

    def test_user_model(self):
      '''Test creating a user instance - no methods.'''

      test_user = User( username = "test_user", password = "password_test", schoole_name = "Springboard", field_of_study = "Software Dev")

      db.sesion.add("test_user")
      db.session.commit()

      self.assertEqual(test_user.username, "test_user")
      self.assertEqual(test_user.school_name, "Springboard")
      self.assertEqual(test_user.field_of_study, "Software Dev")

    #      #      #      #      #      #      #      #      #      #  


    def test_user_missing_data(self):
        '''Test creating a user instance (no methods) with missing data.'''

        test_user = User( username = "test_user", password = "password_test", schoole_name = "Springboard")

        db.sesion.add("test_user")
        db.session.commit()

        self.assertIsNotInstance(test_user, User)

    #      #      #      #      #      #      #      #      #      #  


    def test_user_register(self):
        '''Test creating a user instance using the class register method.'''

        test_user = User.register( username = "test_user", password = "password_test", schoole_name = "Springboard", field_of_study = "Software Dev")

        test_user.id = 456

        db.sesion.add("test_user")
        db.session.commit()

        testing_user = User.query.get(456)

        self.assertIsInstance(testing_user, User)
        self.assertEqual(testing_user.username, "test_user")
        self.assertEqual(testing_user.school_name, "Springboard")
        self.assertEqual(testing_user.field_of_study, "Software Dev")

    #      #      #      #      #      #      #      #      #      #  


    def test_user_register_missing_data(self):
        '''Test creating a user instance using the class register method with missing data.'''

        test_user = User.register( username = "test_user", password = "password_test", schoole_name = "Springboard", field_of_study = "Software Dev")

        db.sesion.add("test_user")
        db.session.commit()

        self.assertIsNotInstance(test_user, User)


    def test_user_authentication(self):
        '''Test using User class method authentication'''

        user = User.authenticate("user1", "password1")

        self.assertIsNotNone(user)
        self.assertIsInstance(user, User)
        self.assertEqual(user.id, self.user1.id)

    #      #      #      #      #      #      #      #      #      #  


    def test_invalid_user(self):
        '''Test incorrect user credentials do not authenticate a user.'''

        attempt_1 = User.authenticate("user1", "wrong_password")
        attempt_2 = User.authenticate("wrong_user", "password2")

        self.assertFalse(attempt_1)
        self.assertFalse(attempt_2)

        







