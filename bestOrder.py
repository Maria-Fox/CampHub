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
        # refirect to the page that this route came from 
        return redirect("/")

    comments = Camphub_Comment.query.all()

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


# COMMENTS SECTION FOR IN-APP 


@app.route("/camphub/comments/all")
def view_camphub_comments():
    '''View comments made here on camphub- does not include Wordpress Comments.'''

    if not g.user:
      return redirect("/")

    all_comments = Camphub_Comment.query.all()
    print("*********************")
    print(all_comments)
    
    return render_template("user_post_routes/camphub_comments.html", all_comments = all_comments)


@app.route("/view/<int:post_id>/<int:comment_id>")
def view_given_comment(post_id, comment_id):
  return "this worked"
    
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


# view one comment

@app.route("/view/<int:post_id>/<int:comment_id>")
def view_given_comment(post_id, comment_id):
  return "this worked"


@app.route("/new/comment/<int:post_id>/<int:user_id>", methods = ["GET", "POST"])
def make_post_comment(post_id, user_id):
      '''Allow authorized user to create a camphub (in-app) comment to an existing in-app post.'''

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


      @app.route("/wordpress/articles/all")
def camphub_posts():
    '''View camphub posts made by moderator/ creator.'''

    if not g.user:
        redirect("/")

    print("********* posts is ****************")

    resp = requests.get(f"{base_url}/{camphub_site}/posts/")
    resp = resp.json()
    
    print("***************************")
    print(resp)

    articles = resp["posts"]
    articles = sorted(articles, key=lambda d: d['date'])

    return render_template("blog_routes/articles.html", articles = articles)

@app.route("/wordpress/camphub/article/<int:article_id>")
def view_article_CH_comment(article_id):
    '''Allow authorized user to view single article/ comments.'''

    form = Wordpress_CH_Article_Comment_Form()


    return render_template("wp_in_app_routes/new_comment.html", form = form)


# for camphub in app comments FOR WORDPRESS- COME BACK AND EDIT
@app.route("/create/comment/<int:article_id>", methods = ["GET", "POST"])
def create_camphub_comment(article_id):
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


    return render_template("wp_in_app_routes/new_comment.html", form = form)


@app.route("/wordpress/comments/<int:article_id>")
def view_wordpress_comment(article_id):
    '''View wordpress replies to given post.'''

    if not g.user:
      return redirect("/")

    post = requests.get(f"{base_url}/{site_id}/posts/{article_id}")
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


# newlist = sorted(list_to_be_sorted, key=lambda d: d['date'])
