from flask_sqlalchemy import SQLAlchemy
# import bcrypt
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey, insert
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    '''Connect to database.'''

    db.app = app
    db.init_app(app)


class User(db.Model):

    def __repr__(self):
        '''Holds user account info.'''
        u = self
        return f"User ID: {u.id}, Contains {u.username}'s password, school name: {u.school_name}, and field of study {u.field_of_study}."

    @classmethod
    def register(cls, username, password, school_name, field_of_study):
        '''Register user with hashed password.'''

        # bcryt.generate_password_hash() is a native flask Brypt method- this salts (introduces random string before hashing) and hashes (1-way transformation of paw) the userpassword. We add this to the db.
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        print("************************************")
        print(hashed_password)
        print("************************************")

        user = User(username = username, password = hashed_password, school_name = school_name, field_of_study = field_of_study)

        db.session.add(user)

        return user

    @classmethod
    def authenticate(cls, username, given_password):
        '''Validate given form data comapred to db.'''

        user = User.query.filter_by(username = username).first()
      
        if user and bcrypt.check_password_hash(user.password, given_password):
            return user
        else:
            return False

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(20), unique = True, nullable =False)
    password = db.Column(db.String, nullable = False)
    school_name = db.Column(db.String, nullable = False)
    field_of_study = db.Column(db.String, nullable = False)

    posts = db.relationship("Camphub_User_Post", cascade="all, delete-orphan")
    comments = db.relationship("Camphub_Comment", cascade="all, delete-orphan")


class Camphub_User_Post(db.Model):
  
    def __repr__(self):
        '''Holds user post information.'''

        p = self
        return f"{p.id} Title: {p.title}, written by user w/ id: {p.author_id}. The post is about {p.content}."

    __tablename__ = "camphub_user_posts"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    title = db.Column(db.String, nullable = False)
    date_time = db.Column(db.DateTime, default = datetime.utcnow(), nullable = False)
    content = db.Column(db.Text, nullable = False)


    users = db.relationship("User")
    camphub_comments = db.relationship("Camphub_Comment", cascade = "all, delete")


class Camphub_Comment(db.Model):

    __tablename__ = "camphub_comments"

    def __repr__(self):
        '''Holds camphub(in-app) comment id, user_id, and content.'''

        c = self
        return f"id: {c.id}, written by {c.comment_user_id}, content: {c.content} "    

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    comment_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    camphub_post_id = db.Column(db.Integer, db.ForeignKey("camphub_user_posts.id"), nullable = False)
    date_time = db.Column(db.DateTime, default = datetime.utcnow(), nullable = False)
    content = db.Column(db.Text, nullable = False) 
    

    users = db.relationship("User")
    posts = db.relationship("Camphub_User_Post")    

class Wordpress_Post_Comment(db.Model):

    __tablename__ = "wordpress_post_comments"

    def __repr__(self):
        '''Holds wordpress article id along with a comment made by the user.'''

        c = self
        return f"id: {c.id}, WP Article id: {c.wordpress_article_id}- Comment made by: {c.user_id}. Content: {c.user_comment}"    

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    wordpress_article_id = db.Column(db.Integer, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    date_time = db.Column(db.DateTime, default = datetime.utcnow(), nullable = False)
    user_comment = db.Column(db.Text, nullable = False) 

    users = db.relationship("User")


# POSSIBLE ADDITION- unsure if I should split it up into article likes and post likes

class User_Like(db.Model):
    """Holds user likes."""

    __tablename__ = 'user_likes'

    def __repr__(self):
        '''Holds wordpress article id along with a comment made by the user.'''

        l = self
        return f"Id: {l.id} for User: {l.user_id}: Optional likes include: user_post_id {l.user_post_id}, comment id: {l.user_comment_id}, WP: article id: {l.wp_article_id}, & WP article comment id: {l.wp_article_comment_id}"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    user_post_id = db.Column(db.Integer, db.ForeignKey("camphub_user_posts.id"),nullable = True)
    user_comment_id = db.Column(db.Integer, db.ForeignKey("camphub_comments.id"), nullable = True)
    # I NEED TO ACCESS THE ARTICLE _ID- BUT IT CANNOT BE A PRIMARY KEY IN THE WP_POST_COMMENTS TABLE- SO, MAYBE USE RELATIONSHIP?
    wp_article_id = db.Column(db.Integer, nullable = True)
    wp_article_comment_id = db.Column(db.Integer, db.ForeignKey("wordpress_post_comments.id"), nullable = True)

    users = db.relationship("User", backref = "user_likes")
    user_posts = db.relationship("Camphub_User_Post", backref = "user_post_likes")
    user_comments = db.relationship("Camphub_Comment", backref = "user_comment_likes")
    wordpress_post_comments = db.relationship("Wordpress_Post_Comment", backref = "wordpress_post_likes")
