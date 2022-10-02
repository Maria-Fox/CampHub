"""Camphub comment view tests."""
# To run tests: python3 -m unittest tests/views/test_user_post_comment_views.py

from unittest import TestCase

from models import  db, User, Camphub_User_Post, Camphub_Comment, Wordpress_Post_Comment
import os

os.environ['DATABASE_URL'] = "postgresql:///camphub_test"

base_url = "https://public-api.wordpress.com/rest/v1.1/sites"
camphub_site = "camphub2022.wordpress.com"
site_id = 210640995
# CURR_USER_KEY is the user.id assigned to session once an acct is created.
from app import app, CURR_USER_KEY

db.create_all()

# The forms are created using WTForms- removing the CSRF token to allow for testing.
app.config['ETF_CSRF_ENABLED'] = False
app.config["TESTING"] = True

class WordpressCommentRoutes(TestCase):
    '''Test camphub comment model. '''

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.register(
            username = "user1",
            password = "password1",
            school_name = "Springboard",
            field_of_study = "Software Engineering"
        )

        user1.id = 888

        db.session.add(user1)
        db.session.commit()

        self.user1 = user1
        self.client = app.test_client()

        #             user1_wordpress_comment = Wordpress_Post_Comment(wordpress_article_id = 8, user_id = 888, user_comment = "This would be a comment on the Wordpress article w/ ID 8.")

        # user1_wordpress_comment.id = 6543

        # db.sesssion.add(user1_wordpress_comment)
        # db.session.commit()

    def tearDown(self):
        """Clean up transactions."""
        db.session.rollback()

    #      #      #      #      #      #      #      #      #      # 

    def test_viewing_wordpress_articles(self):
        '''Testing viewing all wordpress articles.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get(f"/wordpress/articles/all")

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class = "pg-header">Wordpress Articles</h1>', html)


    #      #      #      #      #      #      #      #      #      # 

    def test_viewing_single_article(self):
        '''Testing viewing valid single wordpress article.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            # hard coding 8. Again, it is a confrimed article ID - see tests/models/test_wordpress_post_comments.py for further details.

            resp = c.get(f"/wordpress/camphub/article/8")

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="type-of-comment">CampHub Comments</h2>', html)

    #      #      #      #      #      #      #      #      #      # 


    def test_viewing_invalid_article(self):
        '''Testing viewing invalid wordpress article.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get("/wordpress/camphub/article/9876", follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class = "pg-header">Wordpress Articles</h1>', html)


    #      #      #      #      #      #      #      #      #      # 

    # def test_creating_article_comment(self):
    #     '''Test creating a valid comment on wordpress article.'''

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.user1.id
            
    #         # hard coding article_id as 8. See tests/models/test_wordpress_post_comments.py for further details.

    #         article = c.get(f"{base_url}/{camphub_site}/posts/8")
    #         resp = c.post("create/comment/8", data = {"user_id": self.user1.id, "wordpress_article_id": 8, "user_comment": "This comment is being made by user 1."}, follow_redirects = True)

    #         html = resp.get_data(as_text = True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('<h2 class="type-of-comment">CampHub Comments</h2>', html)
    #         wordpress_comments = Wordpress_Post_Comment.query.filter_by(wordpress_article_id = 8).all()
    #         self.assertEqual(len(wordpress_comments), 2)


    #      #      #      #      #      #      #      #      #      # 

    # def test_deleting_article_comment(self):
    #     '''Test deleting a valid existing wordpress comment id.'''

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.user1.id
    #         # hard coding article_id as 8. See tests/models/test_wordpress_post_comments.py for further details.
            
    #         resp = c.post(f"/wordpress/delete/8/{self.user1_wordpress_comment.id}", follow_redirects = True)

    #         html = resp.get_data(as_text = True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('<title>Wordpress Article</title>', html)
    #         self.assertIn('<li>Deleted comment!</li>', html)
    #         wordpress_comments = Wordpress_Post_Comment.query.all()
    #         self.assertEqual(len(wordpress_comments), 0) 

    # #      #      #      #      #      #      #      #      #      # 

    # def test_deleting_invalid_article_comment(self):
    #     '''Test deleting an invalid wordpress comment id.'''

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.user1.id

    #         # hard coding an invalid article_id and comment_id
    #         resp = c.get(f"/wordpress/delete/78946/789", follow_redirects = True)

    #         html = resp.get_data(as_text = True)

    #         # self.assertEqual(resp.status_code, 200)
    #         self.assertIn('<h1 class = "pg-header">Wordpress Articles</h1>', html)