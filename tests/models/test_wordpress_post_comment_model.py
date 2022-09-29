"""Camphub IN-APP wordpress comments- model tests."""

# To run tests: python3 -m unittest tests/models/test_wordpress_post_comment_model.py. 

# **********IMPORTANT**********: This is a unique class. Typically, this would require a valid Wordpress article id (obtained in app.py through API/http requests & tested for there). Since the goal here is to test the class and not the http requests we will move forward in testing the original two articles leaving us with two confirmed id's: Id: 8 and ID: 13. An additional test will be run against a non-existing article-id, ex: ID: 9999.

from unittest import TestCase
from pyparsing import Word
from models import db, User, Wordpress_Post_Comment
import os

os.environ['DATABASE_URL'] = "postgresql:///camphub_test"

from app import app 
db.create_all()

class CamphubWordpressPostComment(TestCase):
    '''Test in-app wordpress_post_comment class/ test case. '''

    def set_up(self):
      '''Create test client and test user.'''

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

        self.u1 = u1
        self.u2 = u2
        self.article_id = 8

        self.client = app.test_client()

    def tearDown(self):
        """Clean up transactions."""
        db.session.rollback()

    #      #      #      #      #      #      #      #      #      #  


    def test_create_wp_post_comment(self):
        '''Test creating a wordpress_post_comment instance with all input.'''

        test_user_comment = Wordpress_Post_Comment(user_id = self.u1.id, wordpress_article_id = self.article_id, user_comment = "This would be a valid comment under the article w/ id: 8." )

        test_user_comment.id = 852

        db.session.add(test_user_comment)
        db.session.commit()

        comment = Wordpress_Post_Comment.query.get(852)

        self.assertIsInstance(test_user_comment, Wordpress_Post_Comment)
        self.assertEqual(test_user_comment.user_id, self.u1.id)
        self.assertEqual(comment.wordpress_article_id, 8)
        self.assertEqual(comment.user_comment, "This would be a valid comment under the article w/ id: 8.") 

    #      #      #      #      #      #      #      #      #      #  


    # def test_invalid_article_id(self):
    #     '''Test creating a post w/ invalid article id.- See important note above for questions.'''

    #     invalid_article_id_comment = Wordpress_Post_Comment(user_id = self.u1.id, wordpress_article_id = 9999, user_content = "This would fail due to article id not existing in Wordpress.")

    #     db.session.add(invalid_article_id_comment)
    #     db.session.commit()

    #     self.assertNotIsInstance(invalid_article_id_comment, Wordpress_Post_Comment)
        
    # #      #      #      #      #      #      #      #      #      #  



