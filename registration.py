#! /usr/bin/python

from sqlalchemy import create_engine

from sqlalchemy.orm import scoped_session, sessionmaker
import os

engine=create_engine(os.getenv("DATABASE_URL"))
db=scoped_session(sessionmaker(bind=engine))

def main():
    #db.execute("DROP TABLE reviews")
    #db.execute("DROP TABLE users")
    db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY NOT NULL, user_name VARCHAR, email_id VARCHAR NOT NULL, password VARCHAR NOT NULL)")
    db.execute("CREATE TABLE reviews (id SERIAL PRIMARY KEY NOT NULL, rating INT, review VARCHAR, book_id INTEGER REFERENCES books NOT NULL, user_id INTEGER REFERENCES users NOT NULL)")
    db.commit()

if __name__=="__main__":
    main()


