#! /usr/bin/python

from sqlalchemy import create_engine, func, or_
from sqlalchemy.orm import scoped_session, sessionmaker
import os
from flask import Flask, render_template, request,session, redirect, url_for, jsonify
from flask_session import Session
import re
import requests
from models import *
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'njenfjw38uei3jfi3wjfi3fu'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = 'filesystem'


db.init_app(app)
migrate = Migrate(app, db)

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
    
    query = query.lower()

    search_results = Books.query.filter(or_(func.lower(Books.author).like('%{}%'.format(query)), func.lower(Books.isbn).like('%{}%'.format(query)), func.lower(Books.title).like('%{}%'.format(query)))).all()

    if search_results is None:
        return render_template("error.html",message="Invalid Search")
    else:
        return render_template("searcher.html", search_results = search_results)


#    if db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:query) OR LOWER(title) LIKE LOWER(:query) OR LOWER(isbn) LIKE LOWER(:query)",{"query":"%"+query+"%"}).rowcount == 0:
#           return render_template("error.html",message="Invalid Search")
#    search_results = db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:query) OR LOWER(title) LIKE LOWER(:query) or LOWER(isbn) LIKE LOWER(:query)",{"query":"%"+query+"%"}).fetchall() 
#    return render_template("searcher.html",search_results=search_results)

def book(book_id):
    book = Books.query.get(book_id)
    if book is None:
        return render_template("error.html", message = "Book Not Found")
    reviews = book.review
    #book = db.execute("SELECT * FROM books WHERE id = :book_id",{"book_id":book_id}).fetchone()
    #if book is None:
    #    return render_template("error.html",message="Book Not Found")
    #reviews = db.execute("SELECT * FROM reviews WHERE book_id=:book_id",{"book_id":book_id}).fetchall()
    #print(book)
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={'key':'n5BiEwEWALWouvjZBJkj1Q', 'isbns':book.isbn})
    if res.status_code != 200:
        raise Exception("Error connecting to Goodreads!")
    data = res.json()
    goodreads_data = {'work_rating_count':data["books"][0]["work_ratings_count"],'average_rating': data["books"][0]["average_rating"]}
    return render_template("book.html", book=book, review=reviews, goodreads=goodreads_data, user = session["user_id"])

@app.route("/book/<int:book_id>", methods=["POST","GET"])
def review(book_id):
    rate = request.form.get("rate")
    review = request.form.get("review")

    if session.get("user_id"):
        if rate or review:
            book_1 = Books.query.get(book_id)
            book_1.add_review(rate, review, session["id"])
#            db.execute("INSERT INTO reviews (rating, review, book_id, user_id) VALUES (:rate, :review,:book_id,:user_id)", {"rate":rate, "review":review,"book_id":book_id,"user_id":session["id"]})
    else:
        return render_template("error.html", message="Please Log In First")
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={'key':'n5BiEwEWALWouvjZBJkj1Q', 'isbns':''})
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
    
    user = Users.query.filter(Users.email_id == email).filter(Users.password == pwd).first()
    if user is None:
        return render_template("error.html", message="Email or Password is incorrect")
    #print(user) 
    
    print(user)

    #if db.execute("SELECT * FROM users WHERE email_id=:email and password=:password",{"email":email, "password":pwd}).rowcount == 0:
     #   return render_template("error.html", message="Email or Password is incorrect")
    #user=db.execute("SELECT * FROM users WHERE email_id=:email and password=:password",{"email":email, "password":pwd}).fetchall()
    if session.get("id") is None:
        session["id"] = user.id
        session["user_id"] = user.user_name
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
    unique = Users.query.filter_by(email_id=email).first()
    print(unique)
    if unique is not None:
        return render_template("error.html", message="Email already in Use!")

    #if db.execute("SELECT * FROM users WHERE email_id=:email",{"email":email}).rowcount != 0:
     #   return render_template("error.html", message="Email already in Use!")
    user = Users(user_name=username, email_id = email, password = password)
    db.session.add(user)
    db.session.commit()

#    db.execute("INSERT INTO users (user_name, email_id, password) VALUES (:username,:email,:password)",{"username":username,"email":email,"password":password})
 #   db.commit()
    return render_template("login.html",message="User Successfully Registered")

@app.route("/api/<int:book_id>", methods=["GET"])
def api(book_id):
    book = Books.query.get(book_id)
    #book = db.execute("SELECT * FROM books WHERE id = :book_id",{"book_id":book_id}).fetchone()
    if book is None:
        return jsonify({"error":"Invalid book_id"}), 422
    reviews = Reviews.query.filter_by(book_id=book_id).first()
    #reviews = db.execute("SELECT * FROM reviews WHERE book_id=:book_id",{"book_id":book_id}).fetchall()
    #print(book)
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={'key':'n5BiEwEWALWouvjZBJkj1Q', 'isbns':book.isbn})
    if res.status_code != 200:
        raise Exception("Error connecting to Goodreads!")
    data = res.json()
    return jsonify({
        "title":book.title,
        "author":book.author,
        "year":book.year,
        "isbn":book.isbn,
        "work_rating_count":data["books"][0]["work_ratings_count"],
        "average_rating": data["books"][0]["average_rating"]})



