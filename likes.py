@app.route("/wordpress/like/<int:article_id>", methods = ["POST"])
def add_article_like(article_id):
    '''Like/unlike posts from users other than g.user'''

    if not g.user:
        flash("Please sign in to link articles.",  "danger")
        return redirect("/signup")

    article = Wordpress_Post_Comment.query.filter_by(wordpress_article_id = article_id).first_or_404()

    if not article:
        flash("Article does not exist", danger)
        return redirect(f"/wordpress/camphub/article/{article_id}")


    new_article_like = User_Like(user_id = g.user.id, wp_article_id = article)

    db.session.add(new_article_like)
    db.session.commit()

    flash("Added to likes!")

    return redirect(f"/wordpress/camphub/article/{article_id}")



@app.route("/wordpress/like/<int:wordpress_comment__id>", methods = ["POST"])
def add_article_like(wordpress_comment_id):
    '''Like/unlike posts from users other than g.user'''

    if not g.user:
        flash("Please sign in to link articles.",  "danger")
        return redirect("/signup")

    article = Wordpress_Post_Comment.query.filter_by(wordpress_article_id = article_id).first_or_404()

    if not article:
        flash("Article does not exist", danger)
        return redirect(f"/wordpress/camphub/article/{article_id}")


    new_article_like = User_Like(user_id = g.user.id, wp_article_id = article)

    db.session.add(new_article_like)
    db.session.commit()

    flash("Added to likes!")

    return redirect(f"/wordpress/camphub/article/{article_id}")



 