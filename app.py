import os
import requests

from flask import Flask, session, request, render_template, jsonify
from flask_session import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from bs4 import BeautifulSoup

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("loggedin") is None:
            session["loggedin"] = False
        
        if not session["loggedin"]:
            return render_template("login.html")
        else:
            return render_template("index.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        userInfo = db.execute("SELECT id, username FROM users WHERE username = :username AND password = crypt(:password, password)",{"username":username,"password":password}).first()
        if userInfo is None:
            return render_template("login.html", errorMessage = "User does not exist or password incorrect. Please try again.")
        else:
            session["user_id"] = userInfo[0]
            session["user_name"] = userInfo[1]
            session["loggedin"] = True
            return render_template("index.html", username = session["user_name"])

@app.route("/logout")
def logout():
    session["loggedin"] = False
    return render_template("login.html")
    
@app.route("/index", methods=["GET", "POST"])
def index():
    if not session["loggedin"]:
        return render_template("login.html")
    if request.method == "GET":
        return render_template("index.html", username = session["user_name"])
    if request.method == "POST":
        searchString = request.form.get("searchString")
        paramString = "%"+searchString+"%"
        if len(searchString) < 3:
            paramString = searchString+"%"
        radioSelect = request.form.get("searchType")
        if radioSelect is None:
            return render_template("index.html", 
                                    errorMessage="Error: Please select to search based on ISBN, Title or Author.", 
                                    username = session["user_name"])
        if radioSelect == "isbn":
            results = db.execute("SELECT id, title, author FROM books WHERE UPPER(isbn) LIKE UPPER(:param) ORDER BY isbn",{"param":paramString}).fetchall()
            if len(results) == 0:
                return render_template("index.html", 
                                        resultTitle=f"No matches for {radioSelect}: {searchString}.", 
                                        header=('Title','Author'), 
                                        books = results, 
                                        username = session["user_name"])
            return render_template("index.html", 
                                    resultTitle=f"Matches for {searchString}", 
                                    header=('Title','Author'), 
                                    books = results, 
                                    username = session["user_name"])
        if radioSelect == "author":
            results = db.execute("SELECT id, title, author FROM books WHERE UPPER(author) LIKE UPPER(:param) ORDER BY author",{"param":paramString}).fetchall()
            if len(results) == 0:
                return render_template("index.html", 
                                        resultTitle=f"No matches for {radioSelect}: {searchString}.", 
                                        header=('Title','Author'), 
                                        books = results, 
                                        username = session["user_name"])
            return render_template("index.html", 
                                    resultTitle=f"Matches for {searchString}", 
                                    header=('Title','Author'), 
                                    books = results, 
                                    username = session["user_name"])
        if radioSelect == "title":
            results = db.execute("SELECT id, title, author FROM books WHERE UPPER(title) LIKE UPPER(:param) ORDER BY title",{"param":paramString}).fetchall()
            if len(results) == 0:
                return render_template("index.html", 
                                        resultTitle=f"No matches for {radioSelect}: {searchString}.", 
                                        header=('Title','Author'), 
                                        books = results, 
                                        username = session["user_name"])
            return render_template("index.html", 
                                    resultTitle=f"Matches for {searchString}", 
                                    header=('Title','Author'), 
                                    books = results, 
                                    username = session["user_name"])
        return render_template("index.html", username = session["user_name"])

@app.route("/book/<int:book_id>", methods = ["GET", "POST"])
def book(book_id):
    if not session["loggedin"]:
        return render_template("login.html")
    if request.method == "POST":
        reviewText = request.form.get("userreview")
        reviewRating = request.form.get("userrating")
        updating = bool(request.form.get("update"))
        if updating:
            db.execute("UPDATE reviews SET review = :review, rating = :rating WHERE user_id = :user AND book_id = :book",
                        {"review": reviewText,"rating": reviewRating ,"user":session["user_id"], "book":book_id})
            db.commit()
        else:
            db.execute("INSERT INTO reviews (user_id, book_id, rating, review) VALUES (:user,:book,:rating,:review)",
                        {"review": reviewText,"rating": reviewRating,"user":session["user_id"], "book":book_id})
            db.commit()
    local_reviews = db.execute("SELECT username, rating, review FROM reviews JOIN users ON users.id = reviews.user_id WHERE book_id = :id", {"id":book_id}).fetchall()
    if len(local_reviews) == 0:
        local_reviews.append((None,None,"No reviews submitted. Be the FIRST!"))
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id":book_id}).first()
    if book is None:
        return render_template("error.html", errorMessage = "No such book, please return to the search page and try again.", username = session["user_name"])
    image_url = f"https://covers.openlibrary.org/b/isbn/{book[1]}-L.jpg"
    rating_data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "aIvAP7hbk9tTnNYDr2sIg","isbns": book[1]})
    rating_data = rating_data.json()
    rating_data = rating_data["books"][0]
    desc_data = requests.get("https://www.goodreads.com/book/show.xml", params={"key":"aIvAP7hbk9tTnNYDr2sIg", "id":rating_data["id"], "text_only":"True"})
    desc_soup = BeautifulSoup(desc_data.content,features="html.parser")
    if desc_soup.find("description") is not None:
        #find description in the xml as string
        description = desc_soup.find("description").string
    else:
        description = "Description not available"
    return render_template("book.html", 
                            username = session["user_name"], 
                            bookData = book, 
                            ratingData = rating_data, 
                            reviews = local_reviews, 
                            description = description, 
                            imgsrc = image_url,
                            reviewed = None)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        return render_template("create.html")
    else:
        username = request.form.get("username")
        password1 = request.form.get("password")
        password2 = request.form.get("confirmPassword")
        if not password1 == password2:
            return render_template("create.html", errorMessage = "Passwords did not match. Try again")
        exists = db.execute("SELECT COUNT(*) FROM users WHERE username = :username", {"username": username}).first()
        if exists['count'] != 0:
            return render_template("create.html", errorMessage = "That username already exists. Try a different one.")
        db.execute("INSERT INTO users (username, password) VALUES (:username, crypt(:password,gen_salt('bf')))",{"username":username,"password":password1})
        db.commit()
        return render_template("login.html")

@app.route("/api/<isbn>", methods=["GET"])
def book_api(isbn):
    bookData = db.execute("SELECT title, author, year, isbn, CAST(AVG(rating) AS DECIMAL(3,2)), COUNT(*) FROM reviews INNER JOIN books ON books.id = reviews.book_id WHERE isbn = :isbn GROUP BY title, author, year, isbn",{"isbn":isbn}).first()
    print(bookData)
    if bookData is None:
        return jsonify({"ERROR": "That ISBN is not in the database"}), 404
    return jsonify({
            "title": bookData.title,
            "author": bookData.author,
            "year": bookData.year,
            "isbn": bookData.isbn,
            "review_count": bookData.count,
            "average_score": float(bookData.avg)
    })