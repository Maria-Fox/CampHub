"""Camphub comment model tests."""

# To run tests: python3 -m unittest tests/models/test_camphub_comment_model.py

from unittest import TestCase
from models import db, User, Camphub_User_Post, Camphub_Comment
import os

from app import app 
db.create_all()

os.environ['DATABASE_URL'] = "postgresql:///camphub_test"


class CamphubCommentModelTestCase(TestCase):
    '''Test camphub comment model. '''

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


    def test_create_post_comment(self):
        '''Test creating a user_post instance with all input.'''

        # created by user1 - Must create post in order to comment
        test_user_post = Camphub_User_Post(author_id = self.u1.id, title = "Testing Title", content = "This is where the content would go.")

        test_user_post.id = 444

        db.session.add(test_user_post)
        db.session.commit()

        self.assertIsInstance(test_user_post, Camphub_User_Post)
        self.assertEqual(test_user_post.author_id, self.u1.id)
        self.assertEqual(test_user_post.title, "Testing Title")
        # self.assertEqual(test_user_post.content, "This is where the post content would go") 

      # created by user2, date_time is defaulted to "now" in the model.
        test_comment = Camphub_Comment(comment_user_id = self.u2.id, camphub_post_id = 444, content = "This is the comment added.")

        test_comment.id = 987

        db.session.add(test_comment)
        db.session.commit()

        self.assertIsInstance(test_comment, Camphub_Comment)
        self.assertEqual(test_comment.comment_user_id, self.u2.id)
        self.assertEqual(test_comment.camphub_post_id, 444)
        # self.assertIs(test_comment.content, "This is the comment added.")


  

















