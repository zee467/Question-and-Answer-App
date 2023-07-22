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

def load_current_user():
    g.current_user = None
    if 'user' in session:
        user = session['user']
        db = get_db()
        user_cur = db.execute('SELECT id, name, password, expert, admin FROM users WHERE name = ?', [user])
        g.current_user = user_cur.fetchone()


def get_current_user():
    if 'current_user' not in g:
        load_current_user()
    return g.current_user


@app.route("/")
def index():
    user = get_current_user()

    return render_template("home.html", user=user) 


@app.route("/register", methods=["GET", "POST"])
def register():
    user = get_current_user()

    db = get_db()
    if request.method == "POST":
        name = request.form["name"]
        hashed_password = generate_password_hash(request.form["password"], method="sha256")
        db.execute('insert into users (name, password, expert, admin) values (?, ?, ?, ?)', [name, hashed_password, '0', '0'])
        db.commit()

        # adds the username to session
        session['user'] = name

        # redirects to the home route upon registeration
        return redirect(url_for('index'))

    return render_template("register.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    user = get_current_user()

    db = get_db()
    if request.method == "POST":
        name = request.form['name']
        password = request.form["password"]

        user_cur = db.execute('select id, name, password from users where name = ?', [name])
        user_result = user_cur.fetchone()

        if check_password_hash(user_result['password'], password):
            session['user'] = user_result['name']
            return redirect(url_for('index'))
        else:
            return "<h1>The password is incorrect!"

    return render_template("login.html", user=user)


@app.route("/question")
def question():
    user = get_current_user()

    return render_template("question.html", user=user)

@app.route("/answer")
def answer():
    user = get_current_user()

    return render_template("answer.html", user=user)

@app.route("/ask", methods=["GET", "POST"])
def ask():
    db = get_db()
    user = get_current_user()
    if request.method == "POST":
        question = request.form["question"]
        expert_id = request.form["expert"]
        db.execute("insert into questions (question_text, asked_by_id, expert_id) values (?, ?, ?)", [question, user['id'], expert_id])
        db.commit()

        return redirect(url_for('index'))

    expert_cur = db.execute('select id, name from users where expert = 1')
    expert_results = expert_cur.fetchall()

    return render_template("ask.html", user=user, experts=expert_results)

@app.route("/unanswered")
def unanswered():
    user = get_current_user()

    return render_template("unanswered.html", user=user)

@app.route("/users")
def users():
    user = get_current_user()

    db = get_db()
    user_cur = db.execute('select id, name, expert, admin from users')
    user_results = user_cur.fetchall()

    return render_template("users.html", user=user, users=user_results)

@app.route("/promote/<int:user_id>")
def promote(user_id):
    db = get_db()
    db.execute('update users set expert = 1 where id = ?', [user_id])
    db.commit()

    return redirect(url_for('users'))


@app.route("/logout")
def logout():
    # removes user from session
    session.pop('user', None)
    return redirect(url_for('index'))