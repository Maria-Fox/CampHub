from flask_sqlalchemy import SQLAlchemy
import bcrypt
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey, insert

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
    def authenticate(cls, short_name, given_password):
        '''Validate given form data comapred to db.'''

        user = User.query.filter_by(short_name = short_name).first()
      
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

    posts = db.relationship("User_Post")
    comments = db.relationship("Comment")


class User_Post(db.Model):
  
    def __repr__(self):
        '''Holds user post information.'''

        p = self
        return f"{p.id} Title: {p.title}, written by user w/ id: {p.author_id}. The blog is about {p.content}."

    __tablename__ = "user_posts"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    title = db.Column(db.String, nullable = False)
    content = db.Column(db.Text, nullable = False)

    users = db.relationship("User")
    post_comments = db.relationship("Post_Comment")



class Comment(db.Model):

    __tablename__ = "comments"

    def __repr__(self):
        '''Holds comment id, user_id, and content.'''

        c = self
        return f"id: {c.id}, written by {c.comment_user_id}, content: {c.content} "    

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    comment_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    content = db.Column(db.Text, nullable = False) 

    users = db.relationship("User")
    post_comments = db.relationship("Post_Comment")



class Post_Comment(db.Model):
    '''Maps an id to each comment made on a post.'''

    __tablename__ = "post_comments"

    def __repr__(self):
        '''Holds comment id, user_id, and content.'''

        pc = self
        return f"id: {pc.blog_id}, post {pc.post_id}, comment: {pc.comment_id}  "    

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    post_id = db.Column(db.Integer, db.ForeignKey("user_posts.id"), nullable = False)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable = False)

    posts = db.relationship("User_Post")
    comments = db.relationship("Comment")
    

