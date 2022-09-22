"""Camphub IN-APP wordpress comments- model tests."""

# To run tests: python3 -m unittest tests/models/test_wordpress_post_comment_model.py. 

# **********IMPORTANT**********: This is a unique class. Typically, this would require a valid Wordpress article id (obtained in app.py through API/http requests & tested for there). Since the goal here is to test the class and not the http requests we will move forward in testing the original two articles leaving us with two confirmed id's: Id: 8 and ID: 13. An additional test will be run against a non-existing article-id, ex: ID: 9999.

from unittest import TestCase
from pyparsing import Word
from models import db, User, Wordpress_Post_Comment

app.config['SQLALCHEMY_DATABASE_URI'] = "postgres:///camphub_test"

from app import app 
db.create_all()

class CamphubWordpressPostComment(TestCase):
    '''Test in-app wordpress_post_comment class/ test case. '''

    def set_up(self):
      '''Create test client and test user.'''

      db.drop_all()
      db.create_all()

      user1 = User.register("testUser1", "password1", "Springboard", "Software Engineering")

      user1.id = 888

      db.session.add(user1)
      db.session.commit()

      self.client = app.client()

    def tear_down(self):
      db.session.rollback()

    #      #      #      #      #      #      #      #      #      #  


    def test_create_wp_post_comment(self):
        '''Test creating a wordpress_post_comment instance with all input.'''

        # created by user1. Valid article_id. See Important note above.
        test_user_comment = Wordpress_Post_Comment(user_id = 888, wordpress_article_id = 8, user_comment = "This would be a valid comment under the article w/ id: 8." )

        db.session.add(test_user_comment)
        db.session.commit()

        self.assertIsInstance(test_user_comment, Wordpress_Post_Comment)
        self.assertEqual(test_user_comment.user_id, 888)
        self.assertEqual(test_user_comment.article_id, 8)
        self.assertEqual(test_user_comment.user_content, "This would be a valid comment under the article w/ id: 8") 

    #      #      #      #      #      #      #      #      #      #  


    def test_missing_filed_comment(self):
        '''Test creating a post comment where a required field is left empty.'''

        # missing user_content field- required.
        missing_field_comment = Wordpress_Post_Comment(user_id = 888, wordpress_article_id = 8)

        db.session.add(missing_field_comment)
        db.session.commit()

        self.assertNotIsInstance(missing_field_comment, Wordpress_Post_Comment)

    #      #      #      #      #      #      #      #      #      #  


    def test_invalid_article_id(self):
        '''Test creating a post w/ invalid article id.- See important note above for questions.'''

        invalid_article_id_comment = Wordpress_Post_Comment(user_id = 888, wordpress_article_id = 9999, user_content = "This would fail due to article id not existing in Wordpress.")

        db.session.add(invalid_article_id_comment)
        db.session.commit()

        self.assertNotIsInstance(invalid_article_id_comment, Wordpress_Post_Comment)
        
    #      #      #      #      #      #      #      #      #      #  


    def test_invalid_user_id(self):
        '''Test creating a post comment with invalid user_id. '''

        invalid_user_comment = Wordpress_Post_Comment(user_id = 987, wordpress_article_id = 8, user_commnet = "This user does not exist.")

        db.session.add(invalid_user_comment)
        db.session.commit()

        self.assertNotIsInstance(invalid_user_comment, Wordpress_Post_Comment)
