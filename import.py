#! /usr/bin/python

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
import csv

engine=create_engine(os.getenv("DATABASE_URL"))

db=scoped_session(sessionmaker(bind=engine))

def main():
    f = open("E:/Web Development/project1/books.csv")
    reader = csv.reader(f)
    db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year VARCHAR NOT NULL)")
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn,:title,:author,:year)", {"isbn":isbn,"title":title,"author":author,"year":year})
        print(f"Adding {title} into books")
    db.commit()

if __name__=="__main__":
    main()
