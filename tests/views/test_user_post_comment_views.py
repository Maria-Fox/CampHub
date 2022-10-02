"""Camphub comment view tests."""
# To run tests: python3 -m unittest tests/views/test_user_post_comment_views.py

import os
from unittest import TestCase

from models import  db, User, Camphub_User_Post, Camphub_Comment, Wordpress_Post_Comment
import os

os.environ['DATABASE_URL'] = "postgresql:///camphub_test"

# CURR_USER_KEY is the user.id assigned to session once an acct is created.
from app import app, CURR_USER_KEY

db.create_all()

# The forms are created using WTForms- removing the CSRF token to allow for testing.
app.config['ETF_CSRF_ENABLED'] = False
app.config["TESTING"] = True

class CamphubUserCommentRoutes(TestCase):
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

        user2 = User.register(username = "user2",
            password = "password2",
            school_name = "Springboard",
            field_of_study = "UX Design"
        )

        user2.id = 999

        db.session.add_all([user1, user2])
        db.session.commit()

        self.user1 = user1
        self.user2 = user2

        self.client = app.test_client()

    def tearDown(self):
        """Clean up transactions."""
        db.session.rollback()
                

    #      #      #      #      #      #      #      #      #      #  

    def test_getting_comment_form(self):
        '''Test getting comment form.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            first_post = Camphub_User_Post(author_id = self.user1.id, title = "First Post Made", content = "This is where the content would show.")

            first_post.id = 111

            db.session.add(first_post)
            db.session.commit()

            resp = c.get(f"/create/comment/{first_post.id}/{self.user1.id}")

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<a href="/camphub/users/posts">Users Posts</a>', html)



    #      #      #      #      #      #      #      #      #      #  
# redirecting to create  a new post. Committ is failing?
    def test_posting_camphub_post_comment(self):
        '''Test creating a new comment on a user post.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            first_post = Camphub_User_Post(author_id = self.user1.id, title = "First Post Made", content = "This is where the content would show.")

            first_post.id = 111

            db.session.add(first_post)
            db.session.commit()

            resp = c.post(f"/create/comment/{first_post.id}/{self.user1.id}", data = {"comment_user_id": self.user1.id, "camphub_post_id": first_post.id, "content" : "The first comment to be tested."}, follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            # self.assertIn('<h2 id = "user-comments-header">Comment Section</h2>', html)
            posts = Camphub_User_Post.query.all()
            self.assertEqual(len(posts), 1)
            # comments = Camphub_Comment.query.all()
            # self.assertEqual(len(comments), 1)


    #      #      #      #      #      #      #      #      #      #  


    def test_posting_invalid_user_and_post(self):
        '''Test creating a new post comment with invalid user id.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            # post_id/ user_id - neither exist
            resp = c.post(f"/create/comment/899/8462", follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 404)
            self.assertIn('<title>Page not Found</title>', html)


    #      #      #      #      #      #      #      #      #      #  


    def test_posting_against_invalid_post_id(self):
        '''Test creating a new post comment with invalid user_post id.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.post(f"/create/comment/8956/{self.user1.id}", follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 404)
            self.assertIn('<title>Page not Found</title>', html)


    #      #      #      #      #      #      #      #      #      # 

    def test_posting_without_signin(self):
        '''Test creating a new post comment without being signed in.'''

        with self.client as c:
    
            # post with id: 999 does not exist
            resp = c.post(f"/create/comment/789/{self.user1.id}", follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 id="logo-alone">CampHub <i class="fa-solid fa-campground"></i></h1>', html)


    #      #      #      #      #      #      #      #      #      #  

    def test_deleting_post_user_comment(self):
        '''Test deleting a post with a valid user.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

            post = Camphub_User_Post(author_id = self.user2.id, title = "Sample", content = "This is the POST content.")

            post.id = 123

            comment = Camphub_Comment(comment_user_id = self.user2.id, camphub_post_id = 123, content = "This is the COMMENT content.")

            comment.id = 654

            db.session.add_all([post, comment])
            db.session.commit()

            resp = c.post(f"/camphub/delete/{post.id}/{comment.id}", follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 id = "user-comments-header">Comment Section</h2>', html)


    #      #      #      #      #      #      #      #      #      #  


    def test_deleting_comment__without_signin(self):
        '''Test deleting a post without being signed in/ no session[id].'''

        with self.client as c:               

            resp = c.post(f"/camphub/delete/123/321", follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<title>Sign Up</title>', html)


    #      #      #      #      #      #      #      #      #      # 