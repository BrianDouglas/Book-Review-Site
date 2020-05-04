import os

from flask import Flask, session, request, render_template
from flask_session import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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
        if len(searchString) < 2:
            paramString = searchString+"%"
        radioSelect = request.form.get("searchType")
        if radioSelect is None:
            return render_template("index.html", errorMessage="Error: Please select to search based on ISBN, Title or Author.", username = session["user_name"])
        if radioSelect == "isbn":
            results = db.execute("SELECT id, title, author FROM books WHERE UPPER(isbn) LIKE UPPER(:param) ORDER BY isbn",{"param":paramString}).fetchall()
            if len(results) == 0:
                return render_template("index.html", resultTitle=f"No matches for {radioSelect}: {searchString}.", header=('Title','Author'), books = results, username = session["user_name"])
            return render_template("index.html", resultTitle=f"Matches for {searchString}", header=('Title','Author'), books = results, username = session["user_name"])
        if radioSelect == "author":
            results = db.execute("SELECT id, title, author FROM books WHERE UPPER(author) LIKE UPPER(:param) ORDER BY author",{"param":paramString}).fetchall()
            if len(results) == 0:
                return render_template("index.html", resultTitle=f"No matches for {radioSelect}: {searchString}.", header=('Title','Author'), books = results, username = session["user_name"])
            return render_template("index.html", resultTitle=f"Matches for {searchString}", header=('Title','Author'), books = results, username = session["user_name"])
        if radioSelect == "title":
            results = db.execute("SELECT id, title, author FROM books WHERE UPPER(title) LIKE UPPER(:param) ORDER BY title",{"param":paramString}).fetchall()
            if len(results) == 0:
                return render_template("index.html", resultTitle=f"No matches for {radioSelect}: {searchString}.", header=('Title','Author'), books = results, username = session["user_name"])
            return render_template("index.html", resultTitle=f"Matches for {searchString}", header=('Title','Author'), books = results, username = session["user_name"])
        return render_template("index.html", username = session["user_name"])

@app.route("/book/<int:book_id>")
def book(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id":book_id}).first()
    if book is None:
        return render_template("error.html", errorMessage = "No such book, please return to the search page and try again.")
    return render_template("book.html", username = session["user_name"], bookData = book)

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
