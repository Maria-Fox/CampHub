"""Camphub comment model tests."""

# To run tests: python3 -m unittest tests/models/test_camphub_comment_model.py

from unittest import TestCase
from models import db, User, Camphub_User_Post, Camphub_Comment

app.config['SQLALCHEMY_DATABASE_URI'] = "postgres:///camphub_test"

from app import app 
db.create_all()

class CamphubCommentModelTestCase(TestCase):
    '''Test camphub comment model. '''

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


    def test_create_post_comment(self):
        '''Test creating a user_post instance with all input.'''

        # created by user1 - Must create post in order to comment
        test_user_post = Camphub_User_Post(author_id = 888, title = "Testing Title", content = "This is where the content would go.")

        db.session.add(test_user_post)
        db.session.commit()

        self.assertIsInstance(test_user_post, Camphub_User_Post)
        self.assertEqual(test_user_post.author_id, 888)
        self.assertEqual(test_user_post.title, "Testing Title")
        self.assertEqual(test_user_post.content, "This is where the content would go") 

      # created by user2, date_time is defaulted to "now" in the model.
        test_comment = Camphub_Comment(comment_user_id = 999, camphub_post_id = 456, content = "This is the comment added.")

        db.session.add(test_comment)
        db.session.commit()

        self.assertIsInstance(test_comment, Camphub_Comment)
        self.assertEqual(test_comment.comment_user_id, 999)
        self.assertEqual(test_comment.camphub_post_id, 456)
        self.assertEqual(test_comment.content, "This is the comment added.")

      
    #      #      #      #      #      #      #      #      #      #  

    def test_missing_field_post(self):
        '''Test class instance with (required) missing field data.'''

       # created by user1 - Tested above. Simply checking for instance.
        test_user_post = Camphub_User_Post(author_id = 888, title = "Testing Title", content = "This is where the content would go.")

        test_user_post = 654

        db.session.add(test_user_post)
        db.session.commit()

        self.assertIsInstance(test_user_post, Camphub_User_Post) 

        # made by user 2- missing content field- required
        missing_field_comment = Camphub_Comment(comment_user_id = 999, camphub_post_id = 654)

        self.assertNotIsInstance(missing_field_comment, Camphub_Comment)


    #      #      #      #      #      #      #      #      #      #  

    def test_unaothorized_user(self):
        '''Test unaothrized user creating a user post comment.'''

        # created by user1 - Tested in first function.
        test_user_post = Camphub_User_Post(author_id = 888, title = "User not in DB", content = "The user does not exist.")

        test_user_post = 777

        db.session.add(test_user_post)
        db.session.commit()

        self.assertIsInstance(test_user_post, Camphub_User_Post)

        unauth_comment = Camphub_Comment(comment_user_id = 6, camphub_post_id = 777, content = "User does not exist.")

        self.assertNotIsInstance(unauth_comment, Camphub_Comment)


    #      #      #      #      #      #      #      #      #      #  


    def test_unaothorized_post_id(self):
        '''Test creating a comment instance on a non-existing post.'''

        # intentionally creating a post in function to confirm it will not be posted to just any post available.

        # made by user 1 - tested in first function
        just_bc_post = Camphub_User_Post(author_id = 888, title = "Other Post", content = "This is not the post commented on.")

        just_bc_post.id = 1234

        db.session.add(just_bc_post)
        db.session.commit()

        self.assertIsInstance(just_bc_post, Camphub_User_Post)

        # made by user 2
        attempt_comment = Camphub_Comment(comment_user_id = 999, camphub_post_id = 852, content = "The post_id does not exist in db.")

        self.assertNotIsInstance(attempt_comment, Camphub_Comment)

















