"""Camphub user view tests."""
# To run tests: python3 -m unittest tests/views/test_user_views.py

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

      self.user1 = user1
      self.user2 = user2
      self.client = app.client()

    def tear_down(self):
      db.session.rollback()

    #      #      #      #      #      #      #      #      #      #  
    def test_get_user_signup(self):
      '''Test render signup page'''

      with self.client as c:
          resp = c.get("/signup")

          html = resp.get_data(as_text = True)

          self.assertEqual(resp.status_code, 200)
          self.assertIn("<h2>Notice to User:</h2>", html)

    def test_post_user_signup(self):
        '''Test creating a new user/ post request.'''

        with self.client as c:

            resp = c.post("/signup", data = {"username" : "newestUser", "password": "newpassword", "school_name" : "Springboard", "field_of_study": "ux-design"}, follow_redirects = True)

            html = resp.get_data(as_text = True)

            # or 200 (bc or redirect), if 201 fails, but a new user was created, so I'm thinking 201
            self.assertEqual(resp.status_code, 201)
            self.assertIn("<h3>Why was Camphub created?</h3>", html)
            users = User.query.all()
            self.assertTrue(len(users), 3)

    #      #      #      #      #      #      #      #      #      #  

    def test_get_login(self):
        '''Test getting login page.'''

        with self.client as c:
          
            resp = c.get("/login")

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<form action="/login" , method="post">', html)

  
    #      #      #      #      #      #      #      #      #      #  

    def test_post_login(self):
        '''Test authentication an existing user.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.post("/login", data = {"username": "user1", "password" : "password1"}, follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h3>Why was Camphub created?</h3>", html)

    #      #      #      #      #      #      #      #      #      #  

    def test_post_invalid_credentials(self):
        '''Test invalid credentials.'''

        with self.client as c:
            resp = c.post("/login", data = {"username": "NotRealUser", "password" : "password1"}, follow_redirects = True)

            html = resp.get_data(as_text = True)

        # unless the redirect gives a 200
            self.assertNotEqual(resp.status_code, 200)
            self.assertIn('<div id="login-form">', html)


    #      #      #      #      #      #      #      #      #      #  

    def test_post_nonexistent_user(self):
        '''Test loginging in with non-existent user.'''

        with self.client as c:
            resp = c.post("/login", data = {"username": "NotRealUser", "password" : "acctDoesNotExist"}, follow_redirects = True)

            html = resp.get_data(as_text = True)

        #   unless the redirect gives a 200
            self.assertNotEqual(resp.status_code, 200)
            self.assertIn('<div id="login-form">', html)


   #      #      #      #      #      #      #      #      #      #  


    def test_get_home(self):
      '''Test getting home with valid user.'''

      with self.client as c:
          with c.session_transaction() as sess:
              sess[CURR_USER_KEY] = self.user1.id

          resp = c.get(f"/home/{self.user1.id}")

          html = resp.get_data(as_text = True)

          self.assertEqual(resp.status_code, 200)
          self.assertIn('<h3>Why was Camphub created?</h3>', html)


    #      #      #      #      #      #      #      #      #      #  


    def test_get_home_unauth_user(self):
      '''Test getting home with unauth user.'''

      with self.client as c:
          with c.session_transaction() as sess:
              sess[CURR_USER_KEY] = self.user2.id

          resp = c.get(f"/home/{self.user1.id}", follow_redirects = True)

          html = resp.get_data(as_text = True)

          self.assertEqual(resp.status_code, 200)
          self.assertIn('<h3>Why was Camphub created?</h3>', html)


     #      #      #      #      #      #      #      #      #      #  


    def test_get_home_without_signin(self):
      '''Test getting home with valid user.'''

      with self.client as c:

          resp = c.get(f"/home/{self.user1.id}", follow_redirects = True)

          html = resp.get_data(as_text = True)

          self.assertEqual(resp.status_code, 200)
          self.assertIn('<h2>Notice to User:</h2>', html)


    #      #      #      #      #      #      #      #      #      #  


    def test_get_edit_profile(self):
      '''Test getting profile edit form.'''

      with self.client as c:
          with c.session_transaction() as sess:
              sess[CURR_USER_KEY] = self.user1.id

          resp = c.get(f"/edit/profile{self.user1.id}")

          html = resp.get_data(as_text = True)

          self.assertEqual(resp.status_code, 200)
          self.assertIn('<form action="/edit/profile/{{user.id}}" , method="post">', html)


    #      #      #      #      #      #      #      #      #      #  

    def test_post_edit_profile(self):
        '''Test submitting edit profile form with valid credentials and all fields complete.'''

        with self.client as c:
          with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

          resp = c.post(f"/edit/profile/{self. user1.id}", data = {"username": "updatedUser1", "school_name": "Springboard", "field_of_study": "Software Dev"}, follow_redirects = True)

          html = resp.get_data(as_text = True)

          self.assertEqual(resp.status_code, 200)
          self.assertIn('<h3>Why was Camphub created?</h3>', html)


    #      #      #      #      #      #      #      #      #      #  

    def test_get_edit_profilinvalid_creds(self):
        '''Test submitting edit profile form with invalid credentials.'''

        with self.client as c:
            resp = c.get("/edit/profile/789", follow_redirects = True)

            html = resp.get_data(as_text = True)

            # redirects to the signup pg.
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2>Notice to User:</h2>', html)


    #      #      #      #      #      #      #      #      #      #  

    def test_get_logout(self):
        '''Test logging out..'''

        with self.client as c:
          with c.session_transaction() as sess:
              sess[CURR_USER_KEY] = self.user1.id

          resp = c.get("/logout", follow_redirects = True)

          html = resp.get_data(as_text = True)

          self.assertEqual(resp.status_code, 200)
          self.assertIn('<h2>Notice to User:</h2>', html)

            
   #      #      #      #      #      #      #      #      #      #  

    def test_get_logout_without_user(self):
        '''Test logging out without valid session[id].'''

        with self.client as c:

          resp = c.get("/logout", follow_redirects = True)

          html = resp.get_data(as_text = True)

          # redirects to the signup pg.
          self.assertEqual(resp.status_code, 200)
          self.assertIn('<h2>Notice to User:</h2>', html)

    


