
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