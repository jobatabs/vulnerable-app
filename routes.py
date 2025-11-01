from flask import render_template, redirect, request, abort

from sqlalchemy.sql import text

from app import app
from db import db

import users

@app.route("/")
def index():
    result = db.session.execute(text("SELECT id, title, content FROM posts WHERE visible=TRUE"))
    posts = result.fetchall()
    return render_template("index.html", posts=posts)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html")
    if request.method == "POST":
        query = request.form["text"]
        if len(query) < 1:
            return render_template("error.html", \
                                   error="Please enter a search term.")
        if len(query) > 50:
            return render_template("error.html", \
                                   error="Please keep your search term below 50 characters.")
        #sql = text("SELECT id, title, content \
        #           FROM posts WHERE LOWER(title) LIKE LOWER(:text) OR \
        #           LOWER(content) LIKE LOWER(:text)")
        #result = db.session.execute(sql, {"text":"%"+query+"%"})
        sql = (
            "SELECT id, title, content "
            "FROM posts WHERE LOWER(title) LIKE LOWER('%" + query + "%') OR "
            "LOWER(content) LIKE LOWER('%" + query + "%')"
        )
        result = db.session.execute(text(sql))
        results = result.fetchall()
        return render_template("results.html", results=results)

@app.route("/newpost")
def newpost():
    return render_template("newpost.html")

@app.route("/post")
def post():
    post_id = request.args.get("id")
    sql = text("SELECT posts.title, posts.content, \
               posts.added, posts.updated, users.username \
               FROM posts, users WHERE posts.id=:post_id \
               AND posts.visible=TRUE AND posts.added_by = users.id")
    result = db.session.execute(sql, {"post_id":post_id})
    post_listing = result.fetchall()
    sql = text("SELECT comments.id, users.username, \
               comments.comment, comments.added \
               FROM comments, users WHERE post_id=:post_id \
               AND comments.author = users.id AND visible=TRUE")
    result = db.session.execute(sql, {"post_id":post_id})
    comments = result.fetchall()
    return render_template("post.html", post=post_listing, \
                           comments=comments, id=post_id)

@app.route("/send", methods=["POST"])
def send():
    #if users.invalid_token(request.form["token"]):
    #    abort(403)
    title = request.form["title"]
    content = request.form["content"]
    if len(title) < 1:
        return render_template("error.html", error="Please enter a title for the post.")
    if len(content) < 1:
        return render_template("error.html", error="Please enter a content for the post.")
    if len(title) > 50:
        return render_template("error.html", error="Sorry, the title you provided is too long.")
    if len(content) > 5000:
        return render_template("error.html", \
                               error="Sorry, please keep your content below 5000 characters.")
    sql = text("INSERT INTO posts (title, content, visible, added, updated, added_by) \
               VALUES (:title, :content, TRUE, NOW(), NOW(), :user) RETURNING id")
    result = db.session.execute(sql, {"title":title, \
                                      "content":content, \
                                      "user":users.user_id()})
    db.session.commit()
    return redirect("/")

@app.route("/del")
def deletepages():
    return render_template("del.html")

@app.route("/sendcomment", methods=["POST"])
def sendcomment():
    if users.invalid_token(request.form["token"]):
        abort(403)
    comment = request.form["comment"]
    author = request.form["author"]
    try:
        post_id = int(request.form["post_id"])
    except ValueError:
        # We return a vague error here in case we are being red-teamed.
        return render_template("error.html", \
                               error="Sorry, there was an issue with your request.")
    if len(comment) > 2000:
        return render_template("error.html", \
                               error="Sorry, please keep your comment below 2000 characters.")
    if len(comment) < 1:
        return render_template("error.html", \
                               error="Please write something before posting your comment.")
    sql = text("INSERT INTO comments (post_id, author, comment, visible, added) \
               VALUES (:post_id, :author, :comment, TRUE, NOW())")
    db.session.execute(sql, {"post_id":post_id, "author":author, "comment":comment})
    db.session.commit()
    return redirect(f"/post?id={int(post_id)}")

@app.route("/delcomment", methods=["POST"])
def delcomment():
    if users.invalid_token(request.form["token"]):
        abort(403)
    #if users.is_admin():
    del_id = request.form["id"]
    if len(del_id) < 1:
        return render_template("error.html", \
                            error="Please enter an ID.")
    sql = text("UPDATE comments SET visible=FALSE WHERE comments.id=:del_id")
    db.session.execute(sql, {"del_id":del_id})
    db.session.commit()
    return render_template("error.html", error="Delete successful.")
    #return render_template("error.html", \
    #                            error="You must be an administrator to access this page.")

@app.route("/delpost", methods=["POST"])
def delpost():
    if users.invalid_token(request.form["token"]):
        abort(403)
    #if users.is_admin():
    del_id = request.form["id"]
    if len(del_id) < 1:
        return render_template("error.html", \
                            error="Please enter an ID.")
    sql = text("UPDATE posts SET visible=FALSE WHERE posts.id=:del_id")
    db.session.execute(sql, {"del_id":del_id})
    db.session.commit()
    return render_template("error.html", error="Delete successful.")
    #return render_template("error.html", \
    #                            error="You must be an administrator to access this page.")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("error.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        return users.login(username, password)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        return users.register(username, password)

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")
