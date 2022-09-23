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

      user1_wordpress_comment = Wordpress_Post_Comment(wordpress_article_id = 8, user_id = 888, user_content = "This would be a comment on the Wordpress article w/ ID 8.")

      user1_wordpress_comment.id = 6543

      db.sesssion.add(user1_wordpress_comment)
      db.session.commit()

      self.user1 = user1
      self.user2 = user2
      self.user1_wordpress_comment = user1_wordpress_comment
      self.client = app.client()

    def tear_down(self):
      db.session.rollback()

    #      #      #      #      #      #      #      #      #      # 

    def test_viewing_wordpress_articles(self):
        '''Testing viewing all wordpress articles.'''

        with self.client as c:
            resp = c.get(f"wordpress/aricles/all")

            html = resp.get_resp(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Wordpress Articles</h1>', html)


    #      #      #      #      #      #      #      #      #      # 

    def test_viewing_single_article(self):
        '''Testing viewing single wordpress article.'''

        with self.client as c:
            # hard coding 8. Again, it is a confrimed article ID - see tests/models/test_wordpress_post_comments.py for further details.
            resp = c.get(f"wordpress/camphub/article/8")

            html = resp.get_resp(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<title>Wordpress Article</title>', html)
