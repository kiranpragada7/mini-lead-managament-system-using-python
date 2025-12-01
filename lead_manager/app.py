from flask import Flask, g, render_template, request, jsonify, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path

# ----------------------------- CONFIG ----------------------------
DB_PATH = Path(__file__).parent / "leads.db"

app = Flask(__name__)
app.secret_key = "change_this_secret"


# ----------------------------- DB HELPERS -------------------------
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()

    # Create tables
    db.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "username TEXT UNIQUE NOT NULL, "
        "password TEXT NOT NULL)"
    )

    db.execute(
        "CREATE TABLE IF NOT EXISTS leads ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT NOT NULL, "
        "email TEXT, "
        "company TEXT, "
        "status TEXT DEFAULT 'New')"
    )

    # Create default user
    cur = db.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    if cur.fetchone() is None:
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", generate_password_hash("password"))
        )
        db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


# ----------------------------- AUTH HELPERS -----------------------
def login_user(username):
    session["user"] = username


def logout_user():
    session.pop("user", None)


def current_user():
    return session.get("user")


# ----------------------------- ROUTES -----------------------------
@app.route("/")
def index():
    if not current_user():
        return redirect(url_for("login"))
    return render_template("index.html", user=current_user())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")

    db = get_db()
    row = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if row and check_password_hash(row["password"], password):
        login_user(username)
        return redirect(url_for("index"))

    return render_template("login.html", error="Invalid credentials", username=username)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/api/leads", methods=["GET", "POST"])
def api_leads():
    if not current_user():
        return jsonify({"error": "authentication required"}), 401

    db = get_db()

    if request.method == "GET":
        leads = [dict(row) for row in db.execute("SELECT * FROM leads ORDER BY id DESC")]
        return jsonify(leads)

    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "")
    company = data.get("company", "")
    status = data.get("status", "New")

    if not name:
        return jsonify({"error": "name required"}), 400

    cur = db.execute(
        "INSERT INTO leads (name, email, company, status) VALUES (?, ?, ?, ?)",
        (name, email, company, status)
    )
    db.commit()

    new_lead = dict(db.execute("SELECT * FROM leads WHERE id = ?", (cur.lastrowid,)).fetchone())
    return jsonify(new_lead), 201


# ----------------------------- MAIN -----------------------------
if __name__ == "__main__":

    # Create DB file if missing
    if not DB_PATH.exists():
        DB_PATH.touch()

    # Create tables & default user safely
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "username TEXT UNIQUE NOT NULL, "
        "password TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS leads ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT NOT NULL, "
        "email TEXT, "
        "company TEXT, "
        "status TEXT DEFAULT 'New')"
    )
    cur = conn.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    if cur.fetchone() is None:
        conn.execute("INSERT INTO users (username,password) VALUES (?, ?)",
                     ("admin", generate_password_hash("password")))
    conn.commit()
    conn.close()

    # Run init_db safely inside app context
    with app.app_context():
        init_db()

    # Start server
    app.run(debug=True)
