import os
from functools import wraps

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")


# ---------- Helpers / decorators ----------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def role_required(role):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            if session.get("role") != role:
                return redirect(url_for("index"))
            return view(*args, **kwargs)

        return wrapped

    return decorator


def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "ticketsystem"),
        port=int(os.getenv("DB_PORT", "3306")),
    )


# ---------- Routes ----------
@app.get("/")
@login_required
def index():
    return render_template("index.html")


@app.get("/db-test")
@login_required
def db_test():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return f"DB connection OK ✅ Users in DB: {count}"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        hashed_password = generate_password_hash(password)

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (brukernavn, passord, rolle) VALUES (%s, %s, %s)",
                (username, hashed_password, role),
            )
            conn.commit()
        except Exception:
            cur.close()
            conn.close()
            return "User already exists"

        cur.close()
        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM users WHERE brukernavn = %s", (username,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user["passord"], password):
            session["user_id"] = user["id"]
            session["role"] = user["rolle"]
            return redirect(url_for("index"))

        return "Invalid login"

    return render_template("login.html")


@app.get("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- User: tickets ----------
@app.route("/tickets/new", methods=["GET", "POST"])
@login_required
def new_ticket():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO tickets (bruker_id, tittel, beskrivelse) VALUES (%s, %s, %s)",
            (session["user_id"], title, description),
        )
        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for("my_tickets"))

    return render_template("new_ticket.html")


@app.get("/tickets")
@login_required
def my_tickets():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT id, tittel, status FROM tickets WHERE bruker_id = %s",
        (session["user_id"],),
    )
    tickets = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("tickets.html", tickets=tickets)


# ---------- Drift: admin tickets ----------
@app.get("/admin/tickets")
@role_required("drift")
def admin_tickets():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT
          t.id, t.tittel, t.status, t.behandler_id,
          u.brukernavn AS created_by,
          b.brukernavn AS handler_name
        FROM tickets t
        JOIN users u ON t.bruker_id = u.id
        LEFT JOIN users b ON t.behandler_id = b.id
        ORDER BY t.id DESC
    """)
    tickets = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("admin_tickets.html", tickets=tickets)


@app.post("/admin/tickets/<int:ticket_id>/take")
@role_required("drift")
def take_ticket(ticket_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE tickets SET behandler_id = %s, status = 'under_arbeid' WHERE id = %s AND behandler_id IS NULL",
        (session["user_id"], ticket_id),
    )
    conn.commit()

    cur.close()
    conn.close()
    return redirect(url_for("admin_tickets"))


@app.post("/admin/tickets/<int:ticket_id>/status")
@role_required("drift")
def change_status(ticket_id):
    status = request.form["status"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE tickets SET status = %s WHERE id = %s",
        (status, ticket_id),
    )
    conn.commit()

    cur.close()
    conn.close()
    return redirect(url_for("admin_tickets"))
