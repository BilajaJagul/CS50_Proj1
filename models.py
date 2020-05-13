#! /usr/bin/python

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Books(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key = True)
    isbn = db.Column(db.String, nullable = False)
    title = db.Column(db.String, nullable = False)
    author = db.Column(db.String, nullable = False)
    year = db.Column(db.String, nullable = False)
    review = db.relationship("Reviews", backref="Books", lazy = True)

    def add_review(self, rating, review, user_id):
        r = reviews(rating = rating, review = review, book_id = self.id, user_id = user_id)
        db.session.add(r)
        db.session.commit()



class Reviews(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key = True)
    rating = db.Column(db.Integer, nullable = False)
    review = db.Column(db.String, nullable = False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)


class Users(db.Model):
    __tablename__="users"
    id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String, nullable = False)
    email_id = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)



