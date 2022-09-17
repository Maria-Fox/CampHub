-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- Link to schema: https://app.quickdatabasediagrams.com/#/d/plJ5b1
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.


CREATE TABLE "users" (
    "id" int   NOT NULL,
    "user_name" text   NOT NULL,
    "password" text   NOT NULL,
    "school_name" text   NOT NULL,
    "field_of_study" text   NOT NULL,
    CONSTRAINT "pk_users" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "user_posts" (
    "id" int   NOT NULL,
    "author_id" int   NOT NULL,
    "title" text   NOT NULL,
    "content" text   NOT NULL
);

CREATE TABLE "comments" (
    "id" int   NOT NULL,
    "comment_user_id" int   NOT NULL,
    "content" text   NOT NULL,
    CONSTRAINT "pk_comments" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "post_comments" (
    "id" int   NOT NULL,
    "post_id" int   NOT NULL,
    "comment_id" int   NOT NULL
);

ALTER TABLE "user_posts" ADD CONSTRAINT "fk_user_posts_author_id" FOREIGN KEY("author_id")
REFERENCES "users" ("id");

ALTER TABLE "comments" ADD CONSTRAINT "fk_comments_comment_user_id" FOREIGN KEY("comment_user_id")
REFERENCES "users" ("id");

ALTER TABLE "post_comments" ADD CONSTRAINT "fk_post_comments_post_id" FOREIGN KEY("post_id")
REFERENCES "user_posts" ("id");

ALTER TABLE "post_comments" ADD CONSTRAINT "fk_post_comments_comment_id" FOREIGN KEY("comment_id")
REFERENCES "comments" ("id");

