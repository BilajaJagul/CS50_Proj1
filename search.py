#! /usr/bin/python

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
from flask import Flask, render_template, request,session, redirect, url_for, jsonify
from flask_session import Session
import re
import requests

app = Flask(__name__)
app.config["SESSION"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine=create_engine(os.getenv("DATABASE_URL"))
db=scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if session.get("id"):
        return redirect(url_for('login'))
    session.clear()
    return render_template("login.html")

@app.route("/search_results", methods=["POST"])
def search():
    try:
        query = request.form.get("search")
    except ValueError:
        return render_template("error.html", message="Enter something")

    if db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:query) OR LOWER(title) LIKE LOWER(:query) OR LOWER(isbn) LIKE LOWER(:query)",{"query":"%"+query+"%"}).rowcount == 0:
            return render_template("error.html",message="Invalid Search")
    search_results = db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:query) OR LOWER(title) LIKE LOWER(:query) or LOWER(isbn) LIKE LOWER(:query)",{"query":"%"+query+"%"}).fetchall() 
    return render_template("searcher.html",search_results=search_results)

@app.route("/book/<int:book_id>")
def book(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :book_id",{"book_id":book_id}).fetchone()
    if book is None:
        return render_template("error.html",message="Book Not Found")
    reviews = db.execute("SELECT * FROM reviews WHERE book_id=:book_id",{"book_id":book_id}).fetchall()
    #print(book)
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={'key':'n5BiEwEWALWouvjZBJkj1Q', 'isbns':book[1]})
    if res.status_code != 200:
        raise Exception("Error connecting to Goodreads!")
    data = res.json()
    goodreads_data = {'work_rating_count':data["books"][0]["work_ratings_count"],'average_rating': data["books"][0]["average_rating"]}
    return render_template("book.html", book=book, review=reviews, goodreads=goodreads_data, user = session["user_id"])

@app.route("/book/<int:book_id>", methods=["POST"])
def review(book_id):
    rate = request.form.get("rate")
    review = request.form.get("review")

    if rate or review:
        if session.get("id"):
            db.execute("INSERT INTO reviews (rating, review, book_id, user_id) VALUES (:rate, :review,:book_id,:user_id)", {"rate":rate, "review":review,"book_id":book_id,"user_id":session["id"]})
        else:
            return render_template("error.html", message="Please Log In First")
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={'key':'n5BiEwEWALWouvjZBJkj1Q', 'isbns':''})
    db.commit()


    return book(book_id)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/search",methods=["POST","GET"])
def login():
    if session.get("id") and request.method == "GET":
        return render_template("searcher.html", user=session["user_id"])
    try:
        email = request.form.get("email")
        pwd = request.form.get("password")
    except ValueError:
        return render_template("error.html", message="Email or Password is missing")

    if db.execute("SELECT * FROM users WHERE email_id=:email and password=:password",{"email":email, "password":pwd}).rowcount == 0:
        return render_template("error.html", message="Email or Password is incorrect")
    user=db.execute("SELECT * FROM users WHERE email_id=:email and password=:password",{"email":email, "password":pwd}).fetchall()
    if session.get("id") is None:
        session["id"] = user[0][0]
        session["user_id"] = user[0][1]
    return render_template("searcher.html", user=session["user_id"])


#@app.route("/search", methods=["GET"])
#def nologin():
#    return render_template("error.html",message="Log In First!")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/", methods=["POST"])
def registration():
    try:
        email = request.form.get("email")
        password = request.form.get("password")
    except ValueError:
        return render_template("error.html", message="Email or Password is missing")

    username = request.form.get("username")

    if not username:
        username="Anon"
    if re.search("^[A-Za-z].*@.*\..*", email) is False:
        return render_template("error.html", message="Enter Valid Email")
    if db.execute("SELECT * FROM users WHERE email_id=:email",{"email":email}).rowcount != 0:
        return render_template("error.html", message="Email already in Use!")
    db.execute("INSERT INTO users (user_name, email_id, password) VALUES (:username,:email,:password)",{"username":username,"email":email,"password":password})
    db.commit()
    return render_template("login.html",message="User Successfully Registered")

@app.route("/api/<int:book_id>", methods=["GET"])
def api(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :book_id",{"book_id":book_id}).fetchone()
    if book is None:
        return jsonify({"error":"Invalid flight_id"}), 422
    reviews = db.execute("SELECT * FROM reviews WHERE book_id=:book_id",{"book_id":book_id}).fetchall()
    #print(book)
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={'key':'n5BiEwEWALWouvjZBJkj1Q', 'isbns':book[1]})
    if res.status_code != 200:
        raise Exception("Error connecting to Goodreads!")
    data = res.json()
    return jsonify({
        "title":book[2],
        "author":book[3],
        "year":book[4],
        "isbn":book[1],
        "work_rating_count":data["books"][0]["work_ratings_count"],
        "average_rating": data["books"][0]["average_rating"]})


