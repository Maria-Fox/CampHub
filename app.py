from flask import Flask, render_template, redirect, flash, redirect, session, g, abort, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import requests
from models import db, connect_db, User, Camphub_User_Post, Camphub_Comment, Wordpress_Post_Comment, Suggest_Topic, User_Like
from forms import Signup_Form, Login_Form, Edit_Profile_form, Camphub_Comment_Form, Camphub_User_Post_Form, Wordpress_CH_Article_Comment_Form, Suggest_Topic_Form, Edit_CH_Comment_Form, Edit_Post_Form, Edit_Article_Comment_Form
from sqlalchemy.exc import IntegrityError
import json
import os


app = Flask(__name__)

uri = app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///camphub'))

if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'camhub_key')


toolbar = DebugToolbarExtension(app)
app.config["SQLALCHEMY_ECHO"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False


CURR_USER_KEY = "curr_user"
base_url = "https://public-api.wordpress.com/rest/v1.1/sites"
camphub_site = "camphub2022.wordpress.com"
site_id = 210640995
default_profile_image = "https://images.unsplash.com/photo-1504470695779-75300268aa0e?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80"

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

# # # # # # # # # # # # # # # # # # # # #  Sign up/Signin Routes

@app.route("/")
def app_home():
    '''Home page- routes user to appropriate page.'''

    if g.user:
        return redirect(f"/home/{g.user.id}")

    return redirect("/camphub")

@app.route("/camphub")
def landing_page():
    '''Show landing page.'''

    if g.user:
        return redirect(f"/home/{g.user.id}")

    return render_template("landing_page.html")


@app.route("/camphub/breakdown")
def camphub_info():
    '''Render camphub breakdown.'''

    return render_template("user_routes/whatIs.html")
    

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
            
            # hashes given password to securly store in db. Return new user instance w/ hashed data. Add to db.session.
            user = User.register(username, password, school_name, field_of_study)

            db.session.commit()
            complete_login(user)

            return redirect(f"/home/{user.id}")

        except IntegrityError:
            flash("Username already exists- please choose a new username.")
            return render_template("user_routes/signup.html", form = form)

    return render_template("user_routes/signup.html", form = form)


@app.route("/login", methods = ["GET", "POST"])
def login():
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
                flash(f"Welcome, {user.username}!")
                complete_login(user)

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
    return redirect("/camphub")


@app.route("/edit/profile/<int:user_id>", methods = ["GET", "POST"])
def edit_profile(user_id):
    '''Allow signed in user to edit profile. Redirecct for unauthorized user.'''

    if not g.user:
        redirect("/signup")

    user = User.query.get_or_404(user_id)
    form = Edit_Profile_form(obj = user)

    if form.validate_on_submit():

        try:

            if User.authenticate(user.username, form.password.data):

                user.username = form.username.data 
                user.school_name = form.school_name.data
                user.field_of_study = form.field_of_study.data
                
                db.session.add(user)
                db.session.commit()

                flash("Profile was updated!", "success")
                return redirect(f"/home/{user_id}")

        except:
            flash ("Please check your spelling and try again.")
            return redirect(f"/edit/profile/{user_id}")

    return render_template("user_routes/editProfile.html", form = form, user = user)


@app.route("/delete/user/<int:user_id>", methods = ["POST"])
def delete_user(user_id):
    '''Delete user account.'''

    if not g.user:
        return redirect("/signup")

    user = User.query.get_or_404(user_id)

    if g.user.id != user.id:
        return redirect("/camphub")

    try:
        db.session.delete(user)
        db.session.commit()

        flash("Account was deleted!")
        return redirect("/signup")

    except:
        flash("Unsuccessful attempt, please try again.")
        return redirect(f"/edit/profile/{user_id}")


@app.route("/home/<int:user_id>")
def render_homepage(user_id):
    '''Render home page for authorized users. Otherwise, redirect to welcome pg.'''

    if not g.user:
        return redirect ("/")

    user = User.query.get(user_id)

    if user != g.user:
        return redirect(f"/home/{g.user.id}")

    return render_template("user_routes/home.html")

@app.route("/camphub/direction")
def camphub_direction():
    '''Provide new users option for directions/ assistance on where to go/ what they can do.'''

    return render_template("user_routes/directions.html")


@app.errorhandler(404)
def page_not_found(e):
    '''Return 404 page.'''
    return render_template("404.html"), 404



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

    resp = requests.get(f"{base_url}/{camphub_site}/posts/")
    resp = resp.json()
    
    articles = resp["posts"]

    articles = sorted(articles, key=lambda d: d['date'])

    return render_template("article_routes/articles.html", articles = articles)


@app.route("/wordpress/camphub/article/<int:article_id>")
def view_article_CH_comment(article_id):
    '''Allow authorized user to view single article/ comments.'''

    if not g.user:
        flash("Please signup or login if you have an existing account.")
        return redirect("/signup")

    try:

        resp = requests.get(f"{base_url}/{camphub_site}/posts/{article_id}")
        article = resp.json()

        replies = requests.get(f"{base_url}/{camphub_site}/posts/{article_id}/replies/")
        replies = replies.json()
        replies = replies["comments"]

        user_comments_on_WP_article = Wordpress_Post_Comment.query.filter_by(wordpress_article_id = article_id).all()

        return render_template("wp_in_app_routes/single_article.html", article = article, replies = replies, user_comments_on_WP_article = user_comments_on_WP_article)

    except:
        flash("Please view an existing article from the list below.")
        return redirect("/wordpress/articles/all")



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
            db.session.commit()

            flash("Your comment was added to CampHub comments.")
            return redirect(f"/wordpress/camphub/article/{article_id}")

        except:
            flash("Something went wrong- please try again.")
            return redirect(f"/create/comment/{article_id}")


    return render_template("wp_in_app_routes/new_comment.html", form = form, article = article, article_id = article_id)

@app.route("/wordpress/edit/<int:article_id>/<int:comment_id>", methods = ["GET", "POST"])
def edit_article_comment(article_id, comment_id):
    '''Edit valid article comment.'''

    if not g.user:
        return redirect("/signup")

    comment = Wordpress_Post_Comment.query.get_or_404(comment_id)

    form = Edit_Article_Comment_Form(obj = comment)

    try:
        resp = requests.get(f"{base_url}/{camphub_site}/posts/{article_id}")
        article = resp.json()
        
    except:
        flash("Article does not exist.")
        return redirect("/wordpress/articles/all")

    if form.validate_on_submit():
        try:
            comment.user_comment = form.user_comment.data

            db.session.add(comment)
            db.session.commit()
            
            flash("Updated comment!")
            return redirect(f"/wordpress/camphub/article/{article_id}")

        except:
            flash("Something went wrong- please try again.")
            return redirect(f"/wordpress/camphub/article/{article_id}")

    return render_template("wp_in_app_routes/editComment.html", form = form, article= article, comment = comment)


@app.route("/wordpress/delete/<int:article_id>/<int:comment_id>", methods = ["POST"])
def delete_wordpress_comment(article_id, comment_id):
    '''Delete user in-app wordpress comment.'''

    if not g.user:
        return redirect("/signup")

    comment_to_delete = Wordpress_Post_Comment.query.filter_by(id = comment_id, wordpress_article_id = article_id).first_or_404()

    try:
        db.session.delete(comment_to_delete)
        db.session.commit()
        flash("Deleted comment!")

        return redirect(f"/wordpress/camphub/article/{article_id}")

    except:
        flash("Something went wrong- please try again.")
        return redirect(f"/wordpress/camphub/article/{article_id}")





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

    return render_template("user_post_routes/all_posts.html", all_posts = all_posts)


@app.route("/view/camphub/<int:post_id>")
def view_given_post(post_id):
    '''Display given camphub post to authorized user.'''

    if not g.user:
        flash("Unauothorzed access- please signup, or login if you have an account.")
        return redirect("/signup")

    post = Camphub_User_Post.query.filter_by(id = post_id).first_or_404()

    comments = Camphub_Comment.query.filter_by(camphub_post_id = post_id).all()

    return render_template("user_post_routes/single_post.html", post = post, comments = comments)


@app.route("/create/post/<int:user_id>", methods = ["GET", "POST"])
def create_user_post(user_id):
    '''Allow authorized users to create indiviudal posts on app.'''

    if not g.user:
        return redirect("/")

    user = User.query.get_or_404(user_id)

    form = Camphub_User_Post_Form()

    if form.validate_on_submit():
        try:
        
            author_id = g.user.id
            title = form.title.data
            content = form.content.data

            new_user_post = Camphub_User_Post(author_id = author_id, title = title, content = content)

            db.session.add(new_user_post)
            db.session.commit()

            flash("Your post was added!")
            return redirect("/camphub/users/posts")

        except:

            flash("There was an issue submitting the form. Please try again.")
            return redirect(f"/create/post/{user_id}")


    return render_template("user_post_routes/create_post.html", form = form)


@app.route("/camphub/edit/post/<int:post_id>", methods = ["GET", "POST"])
def edit_user_post(post_id):
    '''Edit valid user post.'''

    if not g.user:
        return redirect("/signup")

    post = Camphub_User_Post.query.get_or_404(post_id)

    if post.author_id != g.user.id:
        flash("Unauthorized Access")
        return redirect("/camphub/users/posts")
    
    form = Edit_Post_Form(obj = post)

    if form.validate_on_submit():
        try:
            post.title = form.title.data
            post.content = form.content.data

            db.session.add(post)
            db.session.commit()

            flash("Updated post!")
            return redirect(f"/view/camphub/{post.id}")
        except:
            flash("Something went wrong- please try again.")
            return redirect(f"/camphub/edit/post/{post_id}")

    return render_template("user_post_routes/editPost.html", form = form, post = post)


@app.route("/camphub/delete/post/<int:post_id>", methods = ["POST"])
def delete_post(post_id):
    '''Delete the given user post and post comments.'''

    if not g.user:
        return redirect("/signup")

    post = Camphub_User_Post.query.filter_by(id = post_id, author_id = g.user.id).first_or_404()

    try: 
        db.session.delete(post)
        db.session.commit()
        flash("Deleted post!")

        return redirect("/camphub/users/posts")

    except:
        flash("Something went wrong- please try again.")
        return redirect("/camphub/users/posts")


# # # # # # # # # # # # # # # # #  # # # # # # # COMMENTS SECTION FOR IN-APP 

# this is for ALL IN APP comments. 
@app.route("/camphub/<int:user_id>/comments/all")
def view_camphub_comments(user_id):
    '''View comments made here on camphub- does not include Wordpress Comments.'''

    if not g.user:
        return redirect("/")

    user = User.query.get_or_404(user_id)

    all_comments = Camphub_Comment.query.all()

    return render_template("user_post_routes/camphub_comments.html", all_comments = all_comments)


@app.route("/create/comment/<int:post_id>/<int:user_id>", methods = ["GET", "POST"])
def make_post_comment(post_id, user_id):
    '''Allow authorized user to create a camphub (in-app) comment to an existing IN-APP post.'''

    if not g.user:
        return redirect("/")

    form = Camphub_Comment_Form()

    post = Camphub_User_Post.query.get_or_404(post_id)
    user = User.query.get_or_404(user_id)

    if form.validate_on_submit():
        try:
            comment_user_id = user_id
            camphub_post_id = post_id
            content = form.content.data

            new_post_comment = Camphub_Comment(comment_user_id = comment_user_id, camphub_post_id = camphub_post_id, content= content)

            db.session.add(new_post_comment)
            db.session.commit()

            flash("Created Comment!")

            return redirect(f"/view/camphub/{post_id}")

        except: 
            flash("Something went wrong - please try again.")
            return redirect(f"/view/camphub/{post_id}")

    return render_template("/user_post_routes/new_comment.html", form = form, post = post)

@app.route("/camphub/edit/<int:post_id>/<int:comment_id>", methods = ["GET", "POST"])
def edit_camphub_comment(post_id, comment_id):
    '''Edit authorized user CampHub comment.'''

    if not g.user:
        return redirect("/signup")

    post = Camphub_User_Post.query.get_or_404(post_id)
    comment = Camphub_Comment.query.get_or_404(comment_id)

    if g.user.id != comment.comment_user_id:
        flash("Unauthorized Access")
        return redirect(f"/view/camphub/{post_id}")

    form = Edit_CH_Comment_Form(obj = comment)

    if form.validate_on_submit():
        try:
        
            comment.content = form.content.data

            db.session.add(comment)
            db.session.commit()

            flash("Comment updated!")
            return redirect(f"/view/camphub/{post_id}")
        except:
            flash("Something went wrong- please try again.")
            return redirect(f"/camphub/edit/{post_id}/{comment_id}")


    return render_template("user_post_routes/editComment.html", form = form, post = post , comment = comment)


@app.route("/camphub/delete/<int:post_id>/<int:comment_id>", methods = ["POST"])
def delete_post_comment(post_id, comment_id):
    '''Delete given comment of given user post.'''

    if not g.user:
        return redirect("/signup")

    delete_comment = Camphub_Comment.query.filter_by(camphub_post_id = post_id, id = comment_id).first_or_404()

    try:
        db.session.delete(delete_comment)
        db.session.commit()
        flash("Comment deleted!")

        return redirect(f"/view/camphub/{post_id}")

    except:
        flash("Something went wrong- please try agaib.")
        return (f"/view/camphub/{post_id}")


# # # # # # # # # # # # # # # # # # # # # # # # Suggest a Topic 

@app.route("/suggest/topic/<int:user_id>", methods = ["GET", "POST"])
def suggest_topic(user_id):
    '''Allow user to suggest a moderator article for discussion. '''

    if not g.user:
        return redirect("/signup")

    user = User.query.get_or_404(user_id)

    if g.user != user:
        return redirect("/")

    form = Suggest_Topic_Form()

    if form.validate_on_submit():
        try :
            topic = form.topic.data
            details = form.details.data

            suggestion = Suggest_Topic(user_id = g.user.id, topic = topic, details = details)

            db.session.add(suggestion)
            db.session.commit()

            flash("Suggestion submitted!")
            return redirect(f"/home/{user_id}")
        except:
            flash("Something went wrong- please try again.")

    return render_template("user_routes/suggestTopic.html", form = form)


