from flask import Flask, render_template, redirect, flash, redirect, session, g, abort, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import requests
from telegraph_api import Telegraph
from models import db, connect_db, User, Camphub_User_Post, Camphub_Comment, Camphub_Post_Comment
from forms import Signup_Form, Login_Form, Edit_Profile_form, Camphub_Comment_Form, Camphub_User_Post_Form
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
# Camphub blog routes
# 
# 
# IN -APP POSTS AND COMMENTS

@app.route("/new/comment/<int:post_id>/<int:user_id>")
def make_post_comment(post_id, user_id):
      '''Allow authorized user to create a camphub (in-app) comment to an existing in-app post.'''

      if not g.user:
          return redirect("/")

      # come back and add 404 page
      post = Camphub_User_Post.query.filter_by(id = post_id).first().or404()
      user = User.query.filter_by(id = user_id).first().or404()

      if not post or user: 
          flash("Post does not exist.")
          return redirect("/camphub/users/posts")

          return redirect("/")

    
# this is for ALL IN comments. 
@app.route("/camphub/comments")
def view_camphub_comments():
    '''View comments made here on camphub- does not include Wordpress Comments.'''

    if not g.user:
      return redirect("/")

    all_comments = Camphub_Comment.query.all()
    print("*********************")
    print(all_comments)
    
    return render_template("comment_routes/camphub_comments.html", all_comments = all_comments)

  
@app.route("/camphub/users/posts")
def view_user_posts():
    '''View all camphub user posts.'''

    if not g.user:
      return redirect("/")

    all_posts = Camphub_User_Post.query.all()
    print("******ALL POSTS ARE*******")
    print(all_posts)

    return render_template("user_post_routes/all_posts.html", all_posts = all_posts)


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





# 
# 
# Wordpress Routes
# 
# 

@app.route("/wordpress/posts/all")
def camphub_posts():
    '''View camphub posts made by moderator/ creator.'''

    if not g.user:
        redirect("/")

    print("********* posts is ****************")

    resp = requests.get(f"{base_url}/{camphub_site}/posts/")
    resp = resp.json()

    # need post ID - link to then another route

    print("***************************")
    print(resp)
    # wordpress_posts = posts['posts']

    author = []
    url = []
    content = []
    title = []
    date = []
    post_id = []
    site = []


    # url = resp['posts'][0]['URL']
    # for i in range(len(resp['posts'])): for all but it prints too many?
    print("******************************")

    for i in range(len(resp['posts'])-1):
      author.append(resp['posts'][i]['author']['nice_name'])
      url.append(resp['posts'][i]['short_URL'])
      date.append(resp['posts'][i]['modified'][:10])
      title.append(resp['posts'][i]['title'])
      content.append(resp['posts'][i]['content'])
      post_id.append(resp['posts'][i]['ID'])
      site.append(resp['posts'][i]['meta']['links']['site'])
      print("*************")
      print(post_id)

    
      # print(i, resp['posts'][i])

      print("****************************")
      print(author, url, date, title, content, post_id, site)
    
    print("**********************")
    return render_template("blog_routes/blog.html", author = author, url = url, date = date, title = title, content = content, post_id = post_id, site = site)



# for camphub in app comments FOR WORDPRESS- COME BACK AND EDIT
@app.route("/create/comment", methods = ["GET", "POST"])
def create_camphub_comment():
    '''Create new camphub comment - EXCLUSIVELY ON MODERATOR POSTS.'''

    if not g.user:
      redirect("/")
      
    # come nack and create the form, plug in here
    form = ()

    if form.validate_on_submit():

        try: 
          comment_user_id = g.user.id
          content = form.content.data

          new_comment = Camphub_Comment(comment_user_id = comment_user_id, content = content)

          db.session.add(new_comment)
          db.session.commit()

          print("NEW COMMENT IS ************")
          print(new_comment)
          flash("Your comment was added to camphub comments.")
          return redirect("/camphub/comments")

        except:
          flash("Something went wrong- please try again.")
          return redirect("/create/comment")


    return render_template("comment_routes/new_comment.html", form = form)


@app.route("/wordpress/comments")
def wordpress_comments():
    '''View existing Wordpress Camphub comments.'''

    if not g.user:
        redirect("/")

    resp = requests.get(f"{base_url}/{camphub_site}/comments/")
    resp = resp.json()

    wordpress_comments = []
    wp_comment_id = []

    # NEED TO INCLUDE POST ID
    post_id = []

    for i in range(len(resp['comments'])):
      wordpress_comments.append(resp['comments'][i]['raw_content'])
      wp_comment_id.append(resp['comments'][i]["ID"])

    print("*************COMMENTS ARE:")  
    print(wordpress_comments, wp_comment_id)
    print("************LENGTH IS")
    print(len(wordpress_comments), len(wp_comment_id))

    return render_template("comment_routes/wordpress_comments.html", wordpress_comments = wordpress_comments, wp_comment_id = wp_comment_id)


@app.route("/wordpress/comment/<int:post_id>")
def view_wordpress_comment(post_id):
    '''View replies to given post.'''

    if not g.user:
      return redirect("/")

    post = requests.get(f"{base_url}/{site_id}/posts/{post_id}")
    post = post.json()

    author = post['author']['nice_name']
    title =  post['title']
    content = post['content']

    # print("PAY ATT HERE*********************")
    # print(author, title, content)

    comments = requests.get(f"{base_url}/{camphub_site}/posts/{post_id}/replies/")
    comments = comments.json()

    comment_id = []
    comment_content = []


    for i in range(len(comments['comments'])):
      if comments['comments']['status'] == "approved":
        comment_id.push(comments['comments'][i]['ID'])
        comment_content.push(comments['comments'][i]['raw_comment'])

    return render_template("blog_routes/wp_post_comments.html", author = author, title = title, content = content, comment_id = comment_id, comment_content = comment_content)


