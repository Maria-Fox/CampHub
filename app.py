from flask import Flask, render_template, redirect, flash, redirect, session, g, abort, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import requests
from telegraph_api import Telegraph
from models import db, connect_db, User, Camphub_User_Post, Camphub_Comment, Wordpress_Post_Comment, User_Like
from forms import Signup_Form, Login_Form, Edit_Profile_form, Camphub_Comment_Form, Camphub_User_Post_Form, Wordpress_CH_Article_Comment_Form
from sqlalchemy.exc import IntegrityError
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = 'this is a secret'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///camphub'))
toolbar = DebugToolbarExtension(app)
app.config["SQLALCHEMY_ECHO"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CURR_USER_KEY = "curr_user"
base_url = "https://public-api.wordpress.com/rest/v1.1/sites"
camphub_site = "camphub2022.wordpress.com"
site_id = 210640995

# wordpress specifc variables to be later assigned or modified as query's are requested
wordpress_item = ""

connect_db(app)
db.create_all()

# # # # # # # # # # # # # # # # # # # # # # # # # #  login/auth

@app.before_request
def add_user_to_g():
    """If logged in, add current user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        # global variable- this includes the id, name, etc.

    else:
        g.user = None

def complete_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


# def do_logout():
#     """Logout user."""

#     if CURR_USER_KEY in session:
#         del session[CURR_USER_KEY]



# # # # # # # # # # # # # # # # # # # # # # # # # #  Sign up/Signin Routes

@app.route("/")
def app_home():
    '''Home page- routes user to approporiate page.'''

    if g.user:
        return redirect(f"/home/{g.user.id}")

    return redirect("/signup")


@app.route("/signup", methods = ["GET", "POST"])
def signup():
  '''Generates signup form and creates new user upon post request.'''

  form = Signup_Form()

  if form.validate_on_submit():

    try:
        username = form.username.data
        password = form.password.data
        school_name = form.school_name.data
        field_of_study = form.field_of_study.data

        print("******************************")
        # hashes given password to securly store in db. Return new user instance w/ hashed data. Add to db.session.
        user = User.register(username, password, school_name, field_of_study)

        print(user)

        print("******************************")
        print("******************************")

        db.session.commit()

    except IntegrityError:
        flash("Username already exists- please choose a new username.")
        return render_template("user_routes/signup.html", form = form)

    # assigned globally and to session
    session[CURR_USER_KEY] = user.id

    return redirect(f"/home/{user.id}")
  
  return render_template("user_routes/signup.html", form = form)


@app.route("/login", methods = ["GET", "POST"])
def signin():
    '''Render login form. Authenticate login post requests and redirect user to home page.'''

    form = Login_Form()

    if g.user:
        user_id = g.user.id
        return redirect(f"/home/{user_id}")

    if form.validate_on_submit():

        username = form.username.data
        given_password = form.password.data

        user = User.authenticate(username, given_password)
  
        if user:
            flash(f"Welcome {user.username}!")
            complete_login(user)
            # return redirect to whichever route renders the blog itself
            # return redirect(f"blogs/{blog_id}")
            return redirect (f"/home/{user.id}")
        elif not user:
              flash("Incorrect username or password. Please try again.")
              return redirect("/login")

    return render_template("user_routes/login.html", form = form)

@app.route("/logout")
def logout():

    if not g.user:
      return redirect("/signup")

    del session[CURR_USER_KEY]
    return redirect("/signup")


@app.route("/edit/profile/<int:user_id>", methods = ["GET", "POST"])
def edit_profile(user_id):
    '''Allow signed in user to edit profile. Redirecct for unauthorized user.'''

    if not g.user:
        redirect("/signup")

    user = User.query.get_or_404(user_id)
    form = Edit_Profile_form(obj = user)

    if form.validate_on_submit():

      user.username = form.username.data 
      user.school_name = form.school_name.data
      user.field_of_study = form.field_of_study.data

      db.session.add(user)
      db.session.commit()

      return redirect(f"/home/{user_id}")

    return render_template("user_routes/editProfile.html", form = form, user = user)

@app.route("/home/<int:user_id>")
def render_homepage(user_id):
    '''Render home page for authorized users. Otherwise, redirect to welcome pg.'''

    if not g.user:
        return redirect ("/")
  
    return render_template("user_routes/home.html")


# 
# 
# Camphub IN-APP ROUTES
# 
# 


# # # # # # # # # # # # # # # # # # # # POSTS SECTION FOR IN-APP  


@app.route("/camphub/users/posts")
def view_user_posts():
    '''View all camphub user posts.'''

    if not g.user:
      return redirect("/")

    all_posts = Camphub_User_Post.query.all()
    print("******ALL POSTS ARE*******")
    print(all_posts)

    return render_template("user_post_routes/all_posts.html", all_posts = all_posts)

@app.route("/view/camphub/<int:post_id>")
def view_given_post(post_id):
    '''Display given camphub post to authorized user.'''

    if not g.user:
      flash("Unauothorzed access- please signup, or login if you have an account.")
      return redirect("/signup")

    post = Camphub_User_Post.query.filter_by(id = post_id).first_or_404()

    if not post:
        flash("Post does not exist- please try again")
        return redirect("/camphub/users/posts")

    comments = Camphub_Comment.query.filter_by(camphub_post_id = post_id).all()

    return render_template("user_post_routes/single_post.html", post = post, comments = comments)


@app.route("/create/post/<int:user_id>", methods = ["GET", "POST"])
def create_user_post(user_id):
    '''Allow authorized users to create indiviudal posts on app.'''

    if not g.user:
        return redirect("/")

    form = Camphub_User_Post_Form()

    if form.validate_on_submit():
        try:
        
            author_id = g.user.id
            title = form.title.data
            content = form.content.data

            new_user_post = Camphub_User_Post(author_id = author_id, title = title, content = content)

            db.session.add(new_user_post)
            db.session.commit()
            print(" *************** this is the new user post:")
            print(new_user_post)

            flash("Your post was added!")

            return redirect("/camphub/users/posts")

        except:

            flash("There was an issue submitting the form. Please try again.")
            return redirect(f"/create/post/{user_id}")


    return render_template("user_post_routes/create_post.html", form = form)


# # # # # # # # # # # # # # # # # # # # COMMENTS SECTION FOR IN-APP 

# this is for ALL IN APP comments. 
@app.route("/camphub/comments/all")
def view_camphub_comments():
    '''View comments made here on camphub- does not include Wordpress Comments.'''

    if not g.user:
      return redirect("/")

    all_comments = Camphub_Comment.query.all()
    print("*********************")
    print(all_comments)
    
    return render_template("user_post_routes/camphub_comments.html", all_comments = all_comments)


# view one comment- should I have this 

@app.route("/view/<int:post_id>/<int:comment_id>")
def view_given_comment(post_id, comment_id):
  return "this route needs work"


@app.route("/new/comment/<int:post_id>/<int:user_id>", methods = ["GET", "POST"])
def make_post_comment(post_id, user_id):
      '''Allow authorized user to create a camphub (in-app) comment to an existing IN-APP post.'''

      if not g.user:
          return redirect("/")

      # come back and add 404 page
      post = Camphub_User_Post.query.filter_by(id = post_id).first_or_404()
      user = User.query.filter_by(id = user_id).first_or_404()

      form = Camphub_Comment_Form()

      print("*****post and user are")
      # print(post, user)

      if not post and user: 
          flash("Post or user do not exist.")
          return redirect("/camphub/users/posts")

      if form.validate_on_submit():
          try:
              print("form was submitted")
              comment_user_id = user_id
              camphub_post_id = post_id
              content = form.content.data

              print("****************")
              print(comment_user_id, camphub_post_id, content)

              new_post_comment = Camphub_Comment(comment_user_id = comment_user_id, camphub_post_id = camphub_post_id, content= content)

              print("*******new post here")
              print("new_post_comment")

              db.session.add(new_post_comment)
              db.session.commit()
              print("***********NEW COMMENT")
              print(new_post_comment)
              flash("Comment created!")

              return redirect(f"/view/camphub/{post_id}")

          except: 
              flash("Something went wrong - please try again.")
              return redirect(f"/view/camphub/{post_id}")
              
      return render_template("/user_post_routes/new_comment.html", form = form, post = post)


# 
# 
# Wordpress Routes
# 
# 

@app.route("/wordpress/articles/all")
def camphub_posts():
    '''View all camphub articles made by moderator/ creator.'''

    if not g.user:
        redirect("/")

    print("********* posts is ****************")

    resp = requests.get(f"{base_url}/{camphub_site}/posts/")
    resp = resp.json()
    
    print("***************************")
    # print(resp)

    articles = resp["posts"]
    articles = sorted(articles, key=lambda d: d['date'])

    return render_template("article_routes/articles.html", articles = articles)

@app.route("/wordpress/camphub/article/<int:article_id>")
def view_article_CH_comment(article_id):
    '''Allow authorized user to view single article/ comments.'''

    if not g.user:
        flash("Please signup or login if you have an existing account.")
        return redirect("/signup")

    resp = requests.get(f"{base_url}/{camphub_site}/posts/{article_id}")
    article = resp.json()

    replies = requests.get(f"{base_url}/{camphub_site}/posts/{article_id}/replies/")
    replies = replies.json()

    print("*************************")
    print(replies)

    user_comments_on_WP_article = Wordpress_Post_Comment.query.filter_by(wordpress_article_id = article_id).all()

    print("this is in house")
    print(user_comments_on_WP_article)

    print("THIS IS THE RESP OBJ")
    # print(article)

    return render_template("wp_in_app_routes/single_article.html", article = article, replies = replies, user_comments_on_WP_article = user_comments_on_WP_article)


@app.route("/create/comment/<int:article_id>", methods = ["GET", "POST"])
def create_WP_camphub_comment(article_id):
    '''Create new camphub comment - EXCLUSIVELY ON MODERATOR POSTS.'''

    if not g.user:
      redirect("/")

    try:
        resp = requests.get(f"{base_url}/{camphub_site}/posts/{article_id}")
        article = resp.json()
        article_id =article["ID"]
        
    except:
        flash("Article does not exist.")
        return redirect("/wordpress/articles/all")
      
    form = Wordpress_CH_Article_Comment_Form()

    if form.validate_on_submit():

        try: 
          wordpress_article_id = article_id
          user_id = g.user.id
          user_comment = form.user_comment.data

          new_comment = Wordpress_Post_Comment(wordpress_article_id = wordpress_article_id, user_id = user_id, user_comment = user_comment)

          db.session.add(new_comment)
          print(new_comment)
          db.session.commit()

          flash("Your comment was added to camphub comments.")
          return redirect(f"/wordpress/camphub/article/{article_id}")

        except:
          flash("Something went wrong- please try again.")
          return redirect(f"/create/comment/{article_id}")


    return render_template("wp_in_app_routes/new_comment.html", form = form, article = article, article_id = article_id)


