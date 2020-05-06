import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    #skip the header row
    next(reader)
    #counter to track progress for large number of inserts
    count = 0
    for isbn, title, author, year in reader:       
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                {"isbn": isbn, "title": title, "author": author, "year": year})
        count += 1
        print(count)
    db.commit()

if __name__ == "__main__":
    main()