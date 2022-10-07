"""Camphub user post view tests."""
# To run tests: python3 -m unittest tests/views/test_user_post_views.py

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

class CamphubUserPostRoutes(TestCase):
    '''Test user post views. '''

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        db.drop_all()
        db.create_all()

        user1 = User.register(
            username= "user1",
            password = "password1",
            school_name = "Springboard",
            field_of_study = "Software Engineering",
            bio = "This is a test bio for user1",
            profile_image_url = "https://images.unsplash.com/photo-1509515837298-2c67a3933321?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8NXx8bmlnaHQlMjBza3V8ZW58MHx8MHx8&auto=format&fit=crop&w=500&q=60"
        )

        user1.id = 888

        user2 = User.register(username= "user2",
            password = "password2",
            school_name = "Springboard",
            field_of_study = "UX Design",
            bio = "Bio for user2",
            profile_image_url = "https://images.unsplash.com/photo-1509515837298-2c67a3933321?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8NXx8bmlnaHQlMjBza3V8ZW58MHx8MHx8&auto=format&fit=crop&w=500&q=60"
        )

        user2.id = 999

        db.session.commit()

        self.user1= user1
        self.user2= user2

        self.client = app.test_client()

    def tearDown(self):
        """Clean up transactions."""
        db.session.rollback()

    #      #      #      #      #      #      #      #      #      #  

    def test_viewing_all_posts(self):
        '''Test viewing all user_posts.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get("/camphub/users/posts")

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<title>Camphub User Posts</title>', html)

    #      #      #      #      #      #      #      #      #      #  


    def test_viewing_all_posts_no_user(self):
        '''Test viewing all user_posts without being signed in/ session id.'''

        with self.client as c:

            resp = c.get("/camphub/users/posts", follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 id="logo-alone">CampHub <i class="fa-solid fa-campground"></i></h1>', html)


    #      #      #      #      #      #      #      #      #      #  


    def test_viewing_single_post(self):
        '''Test viewing given user_post.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            first_post = Camphub_User_Post(author_id = self.user1.id, title = "First Post Made", content = "This is where the content would show.")

            first_post.id = 111

            db.session.add(first_post)
            db.session.commit()

            resp = c.get(f"/camphub/view/{first_post.id}", follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertIn('<h2 id = "user-comments-header">Comment Section</h2>', html)
            self.assertEqual(resp.status_code, 200)


    #      #      #      #      #      #      #      #      #      #  


    def test_getting_create_post_form(self):
        '''Test getting new post form.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            resp = c.get(f"/create/post/{self.user1.id}")

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<title>Create Post</title>', html)


    #      #      #      #      #      #      #      #      #      #  

# COME BACK THIS IS NOT WORKING 
    def test_posting_create_post_(self):
        '''Testing submitting new post w/ valid user.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.post(f"create/post/{self.user1.id}", data = {"author_id": {self.user1.id}, "title": "Creating a new post!", "content": "Getting some good testing practice, in!"}, follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            # self.assertIn('<h1 class = "post-header"> Camphub User Posts - All </h1>', html) 
            # all_posts = Camphub_User_Post.query.all()
            # self.assertEqual(len(all_posts), 1)  


    #      #      #      #      #      #      #      #      #      #  


    def test_invalid_post_form(self):
        '''Testing submitting new post w/ invalid user.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.post("create/post/639", follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 404)
            self.assertIn('<title>Page not Found</title>', html) 


    #      #      #      #      #      #      #      #      #      #  


    def test_deleting_post(self):
        '''Testing deleting valid post'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            first_post = Camphub_User_Post(author_id = self.user1.id, title = "First Post Made", content = "This is where the content would show.")

            first_post.id = 111

            db.session.add(first_post)
            db.session.commit()

            resp = c.post(f"camphub/delete/post/111", follow_redirects = True)

            html = resp.get_data(as_text = True)
            
            self.assertIn('<title>Camphub User Posts</title>', html) 
            self.assertEqual(resp.status_code, 200)
            posts = Camphub_User_Post.query.all()
            self.assertEqual(len(posts), 0)


    #      #      #      #      #      #      #      #      #      #  


    def test_deleting_post_unauth_user(self):
        '''Testing deleting valid post- without being post creator'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

            resp = c.post(f"camphub/delete/post/{self.first_post.id}", follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 404)
            self.assertIn('<h1> Camphub User Posts - All </h1>', html)
            posts = Camphub_User_Post.query.all()
            self.assertEqual(len(posts), 1) 


    #      #      #      #      #      #      #      #      #      #  


    def test_deleting_post_unauth_user(self):
        '''Testing deleting valid post- without being signed in/ no session[id]..'''

        with self.client as c:

            resp = c.post(f"camphub/delete/post/111", follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="pg-header">Join CampHub</h1>', html)

    