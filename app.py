from flask import Flask, render_template, g, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
import os

app = Flask(__name__)


app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["DEBUG"] = True

# closes down database 
@app.teardown_appcontext
def close_db(err):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()



@app.route("/")
def index():
    # checks if there is a user key in session
    user = session.get('user', None)

    return render_template("home.html", user=user) 


@app.route("/register", methods=["GET", "POST"])
def register():
    db = get_db()
    if request.method == "POST":
        hashed_password = generate_password_hash(request.form["password"], method="sha256")
        db.execute('insert into users (name, password, expert, admin) values (?, ?, ?, ?)', [request.form["name"], hashed_password, '0', '0'])
        db.commit()

        return f"<h1>User created!</h1>"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    db = get_db()
    if request.method == "POST":
        name = request.form['name']
        password = request.form["password"]

        user_cur = db.execute('select id, name, password from users where name = ?', [name])
        user_result = user_cur.fetchone()

        if check_password_hash(user_result['password'], password):
            session['user'] = user_result['name']
            return f"<h1>The password is correct!"
        else:
            return f"<h1>The password is incorrect!"

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


@app.route("/logout")
def logout():
    # removes user from session
    session.pop('user', None)
    return redirect(url_for('index'))