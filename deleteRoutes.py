# The delete option only displays for the post or comment creator. Therefore, we do not need to test whether or not the user is the creator here as well.


@app.route("/camphub/delete/post/<int:post_id>")
def delete_post(post_id)
    '''Delete the given user post and post comments.'''

    if not g.user:
        return redirect("/signup")

    post = Camaphub_User_post.query.filter_by(id = post_id).first_or_404()

    if not post:
        flash("Post does not exist, so it cannot be deleted.")
        return redirect("/camphub/users/posts")

    try: 
        db.session.delete(post)
        db.session.commit()
        flash("Deleted post!")

        return redirect("/camphub/users/posts")

    except:
        flash("Something went wrong- please try again.")
        return redirect("/camphub/users/posts")



@app.route("/camphub/delete/<int:user_id>/<int:post_id>/<int:comment__id>")
def delete_post_comment(post_id, comment_id):
    '''Delete given comment of given user post.'''

    if not g.user:
      return redirect("/signup")

    delete_comment = Camphub_Comment.query.filter_by(camphub_post_id = post_id, id = comment_id).first_or_404()

    if not delete_comment:
      flash("Unable to delete a post or comment that does not exist.")
      return redirect("/camphub/users/posts")

    try:
        db.session.delete(delete_comment)
        db.session.commit()
        flash("Comment deleted!")

        return redirect(f"/view/camphub/{post_id}")

    except:
          flash("Something went wrong- please try agaib.")
          return (f"/view/camphub/{post_id}")


@app.route("/wordpress/delete/<int:article_id>/<int:wp_comment_id>")
def delete_wordpress_comment(article_id, comment_id):
    '''Delete user in-app wordpress comment.'''

    if not g.user:
        return redirect("/signup")

    comment_to_delete = Wordpress_Post_Comments.query.filter_by(id = comment_id, wordpress_article_id = article_id)

    if not comment_to_delete:
      return redirect("/wordpress/articles/all")

    try:
        db.session.delete(comment_to_delete)
        db.session.commit()
        flash("Deleted comment!")

        return redirect(f"/wordpress/camphub/article/{article_id}")

    except:
        flash("Something went wrong- please try again.")
        return redirect(f"/wordpress/camphub/article/{article_id}")

# create button in the edit profile page
@app.route("/delete/user/<int:user_id>")
def delete_user(user_id):
    '''Delete user account.'''

    if not g.user:
        return redirect("/signup")

    try:
        user = User(id = user_id)

        db.session.delete(user)
        db.session.commit()

        flash("Account was deleted!")
        return redirect("/signup")

    except:
        "Unsuccessful attempt, please try again."
        return redirect(f"/edit/profile/{user_id}")






    



