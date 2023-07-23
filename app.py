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
    db = get_db()

    questions_cur = db.execute('select questions.id as question_id, questions.question_text, askers.name as asker_name, experts.name as expert_name from questions join users as askers on askers.id = questions.asked_by_id join users as experts on experts.id = questions.expert_id where questions.answer is not null')
    questions_results = questions_cur.fetchall()

    return render_template("home.html", user=user, questions=questions_results) 


@app.route("/register", methods=["GET", "POST"])
def register():
    user = get_current_user()

    db = get_db()
    if request.method == "POST":
        name = request.form["name"]

        # checks to see if user already exists
        existing_user_cur = db.execute('select id from users where name = ?', [name])
        existing_user = existing_user_cur.fetchone()

        if existing_user:
            return render_template("register.html", error="User already exists!")

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


@app.route("/question/<int:question_id>")
def question(question_id):
    user = get_current_user()
    db = get_db()

    question_info_cur = db.execute('select questions.question_text, questions.answer, askers.name as asker_name, experts.name as expert_name from questions join users as askers on askers.id = questions.asked_by_id join users as experts on experts.id = questions.expert_id where questions.id = ?', [question_id])
    question_info_results = question_info_cur.fetchone()

    return render_template("question.html", user=user, question_info=question_info_results)


@app.route("/answer/<int:question_id>", methods=["GET", "POST"])
def answer(question_id):
    user = get_current_user()

    # redirects the user to the login page if they are not signed in
    if not user:
        return redirect(url_for('login'))
    
    # redirects the user to the home page if the user is not an expert
    if user['expert'] == 0:
        redirect(url_for('index'))
    
    db = get_db()

    if request.method == "POST":
        expert_answer = request.form["answer"]
        db.execute('update questions set answer = ? where id = ?', [expert_answer, question_id])
        db.commit()
        return redirect(url_for('unanswered'))


    question_cur = db.execute('select id, question_text from questions where id = ?', [question_id])
    result = question_cur.fetchone()

    return render_template("answer.html", user=user, result=result)


@app.route("/ask", methods=["GET", "POST"])
def ask():
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))
    
    db = get_db()
    
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

    if not user:
        return redirect(url_for('login'))
    
    if user['expert'] == 0:
        redirect(url_for('index'))


    db = get_db()
    questions_cur = db.execute('select questions.id, questions.question_text, users.name from questions join users on users.id = questions.asked_by_id where questions.answer is null and questions.expert_id = ?', [user['id']])
    question_results = questions_cur.fetchall()

    return render_template("unanswered.html", user=user, questions=question_results)


@app.route("/users")
def users():
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))
    
    # redirects the user to the home page if the user is not an admin
    if user['admin'] == 0:
        redirect(url_for('index'))

    db = get_db()
    user_cur = db.execute('select id, name, expert, admin from users')
    user_results = user_cur.fetchall()

    return render_template("users.html", user=user, users=user_results)


@app.route("/promote/<int:user_id>")
def promote(user_id):
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))
    
    if user['admin'] == 0:
        redirect(url_for('index'))

    
    db = get_db()
    db.execute('update users set expert = 1 where id = ?', [user_id])
    db.commit()

    return redirect(url_for('users'))


@app.route("/logout")
def logout():
    # removes user from session
    session.pop('user', None)
    return redirect(url_for('index'))