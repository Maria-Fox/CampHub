"""Camphub comment view tests."""
# To run tests: python3 -m unittest tests/views/test_user_post_comment_views.py

from unittest import TestCase

from models import  db, User, Camphub_User_Post, Camphub_Comment, Wordpress_Post_Comment
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres:///camphub_test"

# CURR_USER_KEY is the user.id assigned to session once an acct is created.
from app import app, CURR_USER_KEY

db.create_all()

# The forms are created using WTForms- removing the CSRF token to allow for testing.
app.config['ETF_CSRF_ENABLED'] = False
app.config["TESTING"] = True

class CamphubCommentModelTestCase(TestCase):
    '''Test camphub comment model. '''

    def set_up(self):
      '''Create test client and test user.'''

      db.drop_all()
      db.create_all()

      self.client = app.test_client()

      user1 = User.register("user1", "password1", "Springboard", "Software Engineering")
      user2 = User.register("user2", "password2", "Springboard", "Data Science")

      user1.id = 888
      user2.id = 777

      db.session.add.all([user1, user2])
      db.session.commit()

      first_post = Camphub_User_Post(author_id = 888, title = "First Post Made", content = "This is where the content would show.")

      first_post.id = 111

      user2_comment = Camphub_Comment(comment_author_id = 777, camphub_post_id = 111, content = "Content for post number 111.")

      user2_comment.id = 789

      db.sesssion.add(first_post, user2_comment)
      db.session.commit()

      self.user1 = user1
      self.user2 = user2
      self.first_post = first_post
      self.user2_comment = user2_comment
      self.client = app.client()

    def tear_down(self):
      db.session.rollback()


    #      #      #      #      #      #      #      #      #      # 
    # THIS ROUTE MAY BE DELETED IN THE FUTURE 
    def test_viewing_post_comment(self):
        '''Testing viewing existing post comment.'''

        with self.client as c:
            resp = c.get(f"/view/{self.first_post.id}/{self.user2_comment.id}")

            html = resp.get_resp(as_text = True)

            self.assertIsInstance(self.first_post, Camphub_User_Post)
            self.assertIsInstance(self.user2_comment, Camphub_Comment)
            self.assertEqual(self.user2_comment.content, "Content for post number 111")
            self.assertIn("")

    #      #      #      #      #      #      #      #      #      #  

    def test_posting_camphub_post_comment(self):
        '''Test creating a new post comment.'''

        with self.client as c:
            resp = c.post(f"create/comment/{self.first_post.id}/{self.user2.id}", data = {"comment_user_id": self.user2.id, "camphub_post_id": self.first_post.id, "content" : "The first comment to be tested."}, follow_redirects = True)

            html = resp.get_resp(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2>Comment Section</h2>', html)


    #      #      #      #      #      #      #      #      #      #  


    def test_posting_invalid_user_post_comment(self):
        '''Test creating a new post comment with invalid user- assume g.user is active/correct.'''

        with self.client as c:
            # user with id: 8462 does not exist
            resp = c.post(f"create/comment/{self.first_post.id}/8462", follow_redirects = True)

            html = resp.get_resp(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1> Camphub User Posts - All </h1>', html)


    #      #      #      #      #      #      #      #      #      #  

    def test_posting_invalid_post_comment(self):
        '''Test creating a new post comment with invalid user- assume g.user is active/correct.'''

        with self.client as c:
            # post with id: 999 does not exist
            resp = c.post(f"create/comment/999/{self.user1.id}", follow_redirects = True)

            html = resp.get_resp(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1> Camphub User Posts - All </h1>', html)


    #      #      #      #      #      #      #      #      #      #  




