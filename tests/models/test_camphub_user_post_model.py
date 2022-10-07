"""Camphub User Post model tests."""

# To run tests: python3 -m unittest tests/models/test_camphub_user_post_model.py


from unittest import TestCase
from models import db, User, Camphub_User_Post
import os

os.environ['DATABASE_URL'] = "postgresql:///camphub_test"

from app import app 
db.create_all()

class CamphubPostTestCase(TestCase):
    '''Test usnig the camphub_user_post model class. '''

    def setUp(self):
        """Create test client, add sample data."""

        
        db.drop_all()
        db.create_all()

        u1 = User.register(
            username = "user1",
            password = "password1",
            school_name = "Springboard",
            field_of_study = "Software Engineering",
            bio = "This is a test bio for user1",
            profile_image_url = "https://images.unsplash.com/photo-1509515837298-2c67a3933321?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8NXx8bmlnaHQlMjBza3V8ZW58MHx8MHx8&auto=format&fit=crop&w=500&q=60"
        )

        u1.id = 888

        u2 = User.register(username = "user2",
            password = "password2",
            school_name = "Springboard",
            field_of_study = "UX Design",bio = "This is a test bio for user1",
            profile_image_url = "https://images.unsplash.com/photo-1509515837298-2c67a3933321?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8NXx8bmlnaHQlMjBza3V8ZW58MHx8MHx8&auto=format&fit=crop&w=500&q=60"
        )

        u2.id = 999

        db.session.commit()

        self.u1= u1
        self.u2= u2

        self.client = app.test_client()

    def tearDown(self):
        """Clean up transactions."""
        db.session.rollback()

    #      #      #      #      #      #      #      #      #      


    def test_camphub_user_post_model(self):
        '''Test creating a user_post instance with all input.'''

        # created by user1
        test_user_post = Camphub_User_Post(
            author_id = self.u1.id, title = "Testing Title", 
            content = "This is where the content would go.")

        db.session.add(test_user_post)
        db.session.commit()

        self.assertIsInstance(test_user_post, Camphub_User_Post)
        self.assertEqual(test_user_post.author_id, self.u1.id)
        self.assertEqual(test_user_post.title, "Testing Title")
        self.assertEqual(test_user_post.content, "This is where the content would go.")

    #      #      #      #      #      #      #      #      #

