from flask import Flask, render_template, g
from database import get_db


app = Flask(__name__)

# closes down database 
@app.teardown_appcontext
def close_db(err):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close_db()

        

@app.route("/")
def index():
    return render_template("home.html") 


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/question")
def question():
    return render_template("question.html")

@app.route("/answer")
def answer():
    return render_template("answer.html")

@app.route("/ask")
def ask():
    return render_template("ask.html")

@app.route("/unanswered")
def unanswered():
    return render_template("unanswered.html")

@app.route("/users")
def users():
    return render_template("users.html")