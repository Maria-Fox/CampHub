"""Camphub user view tests."""
# To run tests: python3 -m unittest tests/views/test_user_views.py

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

class CamphubUserRoutes(TestCase):
    '''Test user view routes. '''

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

        db.session.commit()
        # u1 = User.query.get(u1.id)
        # u2 = User.query.get(u2.id)

        self.user1 = user1
        self.user2 = user2

        self.client = app.test_client()

    def tearDown(self):
        """Clean up transactions."""
        db.session.rollback()

    #      #      #      #      #      #      #      #      #      #  
    def test_get_user_signup(self):
        '''Test render signup page'''

        with self.client as c:
            resp = c.get("/signup")

        html = resp.get_data(as_text = True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h1 class="pg-header">Join CampHub</h1>', html)

    def test_post_user_signup(self):
        '''Test creating a new user/ post request.'''

        with self.client as c:

            resp = c.post("/signup", data = {"username" : "newestUser", "password": "newpassword", "school_name" : "Springboard", "field_of_study": "ux-design"}, follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            # self.assertIn("<h3>Why was Camphub created?</h3>", html)
            users = User.query.all()
            self.assertTrue(len(users), 3)

    #      #      #      #      #      #      #      #      #      #  

    def test_get_login(self):
        '''Test getting login page.'''

        with self.client as c:
        
            resp = c.get("/login")

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="pg-header" id="signup-title">Login</h1>', html)


    #      #      #      #      #      #      #      #      #      #  

    def test_post_login(self):
        '''Test authentication an existing user.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.post("/login", data = {"username": "user1", "password" : "password1"}, follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 id="home-title">What would you like to do?</h1>', html)

    #      #      #      #      #      #      #      #      #      #  

    def test_post_invalid_credentials(self):
        '''Test invalid credentials.'''

        with self.client as c:
            resp = c.post("/login", data = {"username": "NotRealUser", "password" : "password1"}, follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="pg-header" id="signup-title">Login</h1>', html)


    #      #      #      #      #      #      #      #      #      #  

    def test_post_nonexistent_user(self):
        '''Test loginging in with non-existent user.'''

        with self.client as c:
            resp = c.post("/login", data = {"username": "NotRealUser", "password" : "acctDoesNotExist"}, follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="pg-header" id="signup-title">Login</h1>', html)


#      #      #      #      #      #      #      #      #      #  


    def test_get_home(self):
        '''Test getting home with valid user.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get(f"/home/{self.user1.id}")

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 id="home-title">What would you like to do?</h1>', html)


    #      #      #      #      #      #      #      #      #      #  


    def test_get_home_without_signin(self):
        '''Test getting home without valid signin - but valid user.'''

        with self.client as c:

            resp = c.get(f"/home/{self.user1.id}", follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 id="logo-alone">CampHub <i class="fa-solid fa-campground"></i></h1>', html)


    #      #      #      #      #      #      #      #      #      #  


    def test_get_edit_profile(self):
        '''Test getting profile edit form.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get(f"/edit/profile/{self.user1.id}")

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="pg-header">Update Profile</h1>', html)


    #      #      #      #      #      #      #      #      #      #  

    def test_post_edit_profile(self):
        '''Test submitting edit profile form with valid credentials and all fields complete.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.post(f"/edit/profile/{self. user1.id}", data = {"username": "updatedUser1", "school_name": "Springboard", "field_of_study": "Software Dev", "password": self.user1.password}, follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            # self.assertIn('<h2>Need some direction?</h2>', html)


    #      #      #      #      #      #      #      #      #      #  

    def test_get_logout(self):
        '''Test logging out..'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get("/logout", follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 id="logo-alone">CampHub <i class="fa-solid fa-campground"></i></h1>', html)

            
#      #      #      #      #      #      #      #      #      #  

    def test_get_logout_without_user(self):
        '''Test logging out without valid session[id].'''

        with self.client as c:

            resp = c.get("/logout", follow_redirects = True)

        html = resp.get_data(as_text = True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h1 class="pg-header">Join CampHub</h1>', html)
