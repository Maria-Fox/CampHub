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
        return f"User ID: {u.id}, Contains {u.username}'s password, school name: {u.school_name}, field of study {u.field_of_study}, bio: {u.bio}, optional image {u.profile_image_url}."

    @classmethod
    def register(cls, username, password, school_name, field_of_study, bio, profile_image_url):
        '''Register user with hashed password.'''

        # bcryt.generate_password_hash() is a native flask Brypt method- this salts (introduces random string before hashing) and hashes (1-way transformation of paw) the userpassword. We add this to the db.
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(username = username, password = hashed_password, school_name = school_name, field_of_study = field_of_study, bio = bio, profile_image_url = profile_image_url)

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
    bio = db.Column(db.Text, nullable = True)
    profile_image_url = db.Column(db.String, nullable = True)


    posts = db.relationship("Camphub_User_Post", cascade = "all, delete-orphan")
    comments = db.relationship("Camphub_Comment", cascade = "all, delete-orphan")
    wordpress_comments = db.relationship("Wordpress_Post_Comment", cascade = "all, delete-orphan")
    suggestions = db.relationship("Suggest_Topic", cascade = "all, delete-orphan")

    # separate likes relationships
    ch_post_likes  =  db.relationship("Camphub_User_Post", secondary = "ch_post_likes")
    ch_comment_likes = db.relationship("Camphub_Comment", secondary = "ch_comment_likes")
    ch_article_comment_likes = db.relationship("Wordpress_Post_Comment", secondary = "ch_article_comment_likes")


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

    @property
    def friendly_date(self):
        """Makes the date look user friendly for reading."""
        return self.created_at.strftime("%a %b %-d %Y, %-I:%M %p")


class Camphub_Comment(db.Model):

    __tablename__ = "camphub_comments"

    def __repr__(self):
        '''Holds camphub(in-app) comment id, user_id, and content.'''

        c = self
        return f"id: {c.id}, written by {c.comment_user_id}, content: {c.content} "    

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    comment_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    camphub_post_id = db.Column(db.Integer, db.ForeignKey("camphub_user_posts.id",  ondelete = "CASCADE"), nullable = False)
    date_time = db.Column(db.DateTime, default = datetime.utcnow(), nullable = False)
    content = db.Column(db.Text, nullable = False) 
    

    users = db.relationship("User")
    posts = db.relationship("Camphub_User_Post")  

    @property
    def friendly_date(self):
        """Makes the date look user friendly for reading."""
        return self.created_at.strftime("%a %b %-d %Y, %-I:%M %p")  

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

    @property
    def friendly_date(self):
        """Makes the date look user friendly for reading."""
        return self.created_at.strftime("%a %b %-d %Y, %-I:%M %p")


class Suggest_Topic(db.Model):
    '''Allow users to suggest article topics to be posted by the moderator on the official WordPress blog for discussion in-app and outside.'''

    def __repr__(self):
        '''Allows users to suggest moderator topics.'''

        s = self
        return f"{s.user_id} suggested {s.title}"

    __tablename__ = "suggest_topics"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    topic = db.Column(db.String, nullable = False)
    details = db.Column(db.Text, nullable = False)

    users = db.relationship("User")


# POSSIBLE FUTURE ADDITION

class CH_Post_Like(db.Model):
    """Holds CampHub post likes."""

    __tablename__ = 'ch_post_likes'

    def __repr__(self):
        '''Holds posts liked by given user.'''

        l = self
        return f"Id: {l.id} for User: {l.user_id} on post id: {l.user_post_id}"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = "CASCADE"), nullable = False)
    user_post_id = db.Column(db.Integer, db.ForeignKey("camphub_user_posts.id",ondelete = "CASCADE"), nullable = False)



class CH_Comment_Like(db.Model):
    """Holds CampHub comment likes."""

    __tablename__ = 'ch_comment_likes'

    def __repr__(self):
        '''Holds wordpress article id along with a comment made by the user.'''

        l = self
        return f"Id: {l.id} for User: {l.user_id} on post id: {l.user_comment_id}"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = "CASCADE"), nullable = False)
    user_comment_id = db.Column(db.Integer, db.ForeignKey("camphub_comments.id", ondelete = "CASCADE"), nullable = False)



class CH_Article_Comment_Like(db.Model):
    """Holds CampHub comment likes."""

    __tablename__ = 'ch_article_comment_likes'

    def __repr__(self):
        '''Holds wordpress article id along with a comment made by the user.'''

        l = self
        return f"Id: {l.id} for User: {l.user_id} on post id: {l.wp_article_comment_id}"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = "CASCADE"), nullable = False)
    wp_article_comment_id = db.Column(db.Integer, db.ForeignKey("wordpress_post_comments.id", ondelete = "CASCADE"), nullable = False)

