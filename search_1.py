#! /usr/bin/python

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
from flask import Flask, render_template, request

app = Flask(__name__)

engine=create_engine(os.getenv("DATABASE_URL"))
db=scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("search.html")

@app.route("/search", methods=["POST"])
def search():
    try:
        query = request.form.get("search")
    except ValueError:
        return render_template("error.html", message="Enter something")

    if db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:query) OR LOWER(title) LIKE LOWER(:query) OR LOWER(isbn) LIKE LOWER(:query)",{"query":"%"+query+"%"}).rowcount == 0:
            return render_template("error.html",message="Invalid Search")
    search_results = db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:query) OR LOWER(title) LIKE LOWER(:query) or LOWER(isbn) LIKE LOWER(:query)",{"query":"%"+query+"%"}).fetchall()
    return render_template("search.html",search_results=search_results)



