"""Camphub user post view tests."""
# To run tests: python3 -m unittest tests/views/test_user_post_views.py

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

      db.session.add(first_post)

      self.user1 = user1
      self.user2 = user2
      self.first_post = first_post
      self.client = app.client()
      self.client = app.client()

    def tear_down(self):
      db.session.rollback()

    #      #      #      #      #      #      #      #      #      #  

    def test_viewing_all_posts(self):
        '''Test viewing all user_posts.'''

        with self.client as c:
            resp = c.get("camphub/users/posts")

            html = resp.get_resp(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1> Camphub User Posts - All </h1>', html)


    #      #      #      #      #      #      #      #      #      #  


    def test_viewing_single_post(self):
        '''Test viewing given user_post.'''

        with self.client as c:
            resp = c.get(f"/view/camphub/{self.first_post.id}")

            html = resp.get_resp(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2>Comment Section</h2>', html)


    #      #      #      #      #      #      #      #      #      #  


    def test_viewing_invalid_single_post(self):
        '''Test viewing invalid user_post.'''

        with self.client as c:
            resp = c.get("/view/camphub/73", follow_redirects = True)

            html = resp.get_resp(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1> Camphub User Posts - All </h1>', html)


    #      #      #      #      #      #      #      #      #      #  

    # get and post route

    def test_getting_create_post_form(self):
        '''Test getting new post form.'''

        with self.client as c:
            resp = c.get(f"create/post/{self.user1.id}")

            html = resp.get_resp(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Create a New Post</h1>', html)


    #      #      #      #      #      #      #      #      #      #  


    def test_posting_create_post_(self):
        '''Testing submitting new post w/ valid user.'''

        with self.client as c:
            resp = c.post(f"create/post/{self.user1.id}", data = {"author_id": {self.user1.id}, "title": "Creating a new post!", "content": "Getting some good testing practice, in!"})

            html = resp.get_resp(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1> Camphub User Posts - All </h1>', html)   


    #      #      #      #      #      #      #      #      #      #  


    def test_invalid_post_form(self):
        '''Testing submitting new post w/ invalid user.'''

        with self.client as c:
          # route would be redirected
            resp = c.post("create/post/639", follow_redirects = True)

            html = resp.get_resp(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h3>Why was Camphub created?</h3>', html) 