-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- Link to schema: https://app.quickdatabasediagrams.com/#/d/plJ5b1
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.


CREATE TABLE "users" (
    "id" int   NOT NULL,
    "username" text   NOT NULL,
    "password" text   NOT NULL,
    "school_name" text   NOT NULL,
    "field_of_study" text   NOT NULL,
    CONSTRAINT "pk_users" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "camphub_user_posts" (
    "id" int   NOT NULL,
    "author_id" int   NOT NULL,
    "title" text   NOT NULL,
    "content" text   NOT NULL
);

CREATE TABLE "camphub_comments" (
    "id" int   NOT NULL,
    "comment_user_id" int   NOT NULL,
    "camphub_post_id" int   NOT NULL,
    "content" text   NOT NULL,
    CONSTRAINT "pk_camphub_comments" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "wordpress_post_comments" (
    "id" int   NOT NULL,
    "wordpress_article_id" int   NOT NULL,
    "user_id" int   NOT NULL,
    "user_comment" text   NOT NULL,
    CONSTRAINT "pk_wordpress_post_comments" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "user_likes" (
    "id" int   NOT NULL,
    "user_id" int   NOT NULL,
    "user_post_id" int   NOT NULL,
    "user_comment_id" int   NOT NULL,
    "wp_article_id" int   NOT NULL,
    "wp_article_comment_id" int   NOT NULL,
    CONSTRAINT "pk_user_likes" PRIMARY KEY (
        "id","wp_article_id"
     )
);

ALTER TABLE "camphub_user_posts" ADD CONSTRAINT "fk_camphub_user_posts_author_id" FOREIGN KEY("author_id")
REFERENCES "users" ("id");

ALTER TABLE "camphub_comments" ADD CONSTRAINT "fk_camphub_comments_comment_user_id" FOREIGN KEY("comment_user_id")
REFERENCES "users" ("id");

ALTER TABLE "camphub_comments" ADD CONSTRAINT "fk_camphub_comments_camphub_post_id" FOREIGN KEY("camphub_post_id")
REFERENCES "camphub_user_posts" ("id");

ALTER TABLE "wordpress_post_comments" ADD CONSTRAINT "fk_wordpress_post_comments_user_id" FOREIGN KEY("user_id")
REFERENCES "users" ("id");

ALTER TABLE "user_likes" ADD CONSTRAINT "fk_user_likes_user_id" FOREIGN KEY("user_id")
REFERENCES "users" ("id");

ALTER TABLE "user_likes" ADD CONSTRAINT "fk_user_likes_user_post_id" FOREIGN KEY("user_post_id")
REFERENCES "camphub_user_posts" ("id");

ALTER TABLE "user_likes" ADD CONSTRAINT "fk_user_likes_user_comment_id" FOREIGN KEY("user_comment_id")
REFERENCES "camphub_comments" ("id");

ALTER TABLE "user_likes" ADD CONSTRAINT "fk_user_likes_wp_article_id" FOREIGN KEY("wp_article_id")
REFERENCES "wordpress_post_comments" ("id");

ALTER TABLE "user_likes" ADD CONSTRAINT "fk_user_likes_wp_article_comment_id" FOREIGN KEY("wp_article_comment_id")
REFERENCES "wordpress_post_comments" ("id");

