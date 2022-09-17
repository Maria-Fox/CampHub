from flask import Flask, render_template, redirect, flash, redirect, session, g, abort, request
from flask_debugtoolbar import DebugToolbarExtension
import requests
from telegraph_api import Telegraph
from models import db, connect_db, User, User_Post, Comment, Post_Comment
from forms import Signup_Form, Login_Form, Edit_Profile_form, Create_Post_Form, Comment_Form
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

      user.short_name = form.short_name.data 
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

@app.route("/camphub/posts")
def camphub_posts():
    '''View camphub posts made by moderator/ creator.'''

    if not g.user:
        redirect("/")


    print("********* posts is ****************")
    # resp = requests.get(f"{base_url}/{camphub_site}/")

    # resp = resp.json()
    # wordpress_blog_info = resp

    resp = requests.get(f"{base_url}/{camphub_site}/posts/")
    resp = resp.json()
    # wordpress_posts = posts['posts']

    author = []
    url = []
    content = []
    title = []
    date = []
    post_id = []
    site = []

    # url = resp['posts'][0]['URL']
    print("******************************")

    for i in range(len(resp['posts'])-1):
      author.append(resp['posts'][i]['author']['nice_name'])
      url.append(resp['posts'][i]['short_URL'])
      date.append(resp['posts'][i]['modified'][:10])
      title.append(resp['posts'][i]['title'])
      content.append(resp['posts'][i]['content'])
      post_id.append(resp['posts'][i]['ID'])
      site.append(resp['posts'][i]['meta']['links']['site'])
      # print(i, resp['posts'][i])

      print("****************************")
      print(author, url, date, title, content, post_id, site)
    
    print("**********************")
    return render_template("blog_routes/blog.html", author = author, url = url, date = date, title = title, content = content, post_id = post_id, site = site)
    

@app.route("/wordpress/comments")
def wordpress_comments():
    '''View existing Wordpress Camphub comments.'''

    if not g.user:
      redirect("/")

    resp = requests.get(f"{base_url}/{camphub_site}/comments/")
    resp = resp.json()

    wordpress_comments = []
    wp_comment_id = []

    for i in range(len(resp['comments'])):
      wordpress_comments.append(resp['comments'][i]['raw_content'])
      wp_comment_id.append(resp['comments'][i]["ID"])

    print("*************COMMENTS ARE:")  
    print(wordpress_comments, wp_comment_id)
    print("************LENGTH IS")
    print(len(wordpress_comments), len(wp_comment_id))

    return render_template("comment_routes/wordpress_comments.html", wordpress_comments = wordpress_comments, wp_comment_id = wp_comment_id)


@app.route("/wordpress/view/comment/")
def view_wordpress_comment(id):
    '''View replies to given post.'''

    resp = requests.get(f"{base_url}/sites/{site_id}/")
    # https://public-api.wordpress.com/rest/v1.1/sites/210640995/posts/13/replies/

    return

@app.route("/create/comment")
def camphub_comment():
    '''Create new camphub comment.'''

    if not g.user:
      redirect("/")

    form = Create_Post_Form()

    if form.validate_on_submit():

        comment_user_id = g.user.id
        content = form.content.data

        new_comment = Comment(comment_user_id = comment_user_id, content = content)

        return 

    return render_template("comment_routes/new_comment.html", form = form)