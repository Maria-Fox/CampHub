"""Camphub User Post model tests."""

# To run tests: python3 -m unittest tests/models/test_camphub_user_post_model.py


from unittest import TestCase
from models import db, User, Camphub_User_Post

app.config['SQLALCHEMY_DATABASE_URI'] = "postgres:///camphub_test"

from app import app 
db.create_all()

class CamphubUserPostModelTestCase(TestCase):
    '''Test camphub user post class. '''

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

    def test_camphub_user_post_model(self):
      '''Test creating a user_post instance with all input.'''

      # created by user1
      test_user_post = Camphub_User_Post(author_id = 888, title = "Testing Title", content = "This is where the content would go.")

      db.sesion.add("test_user_post")
      db.session.commit()

      self.assertIsInstance(test_user_post, Camphub_User_Post)
      self.assertEqual(test_user_post.author_id, 888)
      self.assertEqual(test_user_post.title, "Testing Title")
      self.assertEqual(test_user_post.content, "This is where the content would go")
  
  #      #      #      #      #      #      #      #      #      #  


    def test_camphub_post_missing_field(self):
        '''Test creating a user_post instance where a necessary data field was left empty.'''

        # created by user2, no title submitted
        test_user_post = Camphub_User_Post(author_id = 999, content = "This is where the content would go.")

        db.sesion.add("test_user_post")
        db.session.commit()

        self.assertNotIsInstance(test_user_post, Camphub_User_Post)

  #      #      #      #      #      #      #      #      #      #  



    def test_camphub_post_unauthorized(self):
        '''Test creating a user_post instance where user does not exist.'''

        test_user_post = Camphub_User_Post(author_id = 24, title = "Testing Title", content = "This is where the content would go.")

        db.sesion.add("test_user_post")
        db.session.commit()


        self.assertNotIsInstance(test_user_post, Camphub_User_Post) 