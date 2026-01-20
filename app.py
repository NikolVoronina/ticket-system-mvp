from flask import request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash


import os
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")


def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "ticketsystem"),
        port=int(os.getenv("DB_PORT", "3306")),
    )


@app.get("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")



@app.get("/db-test")
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

        cur.execute(
            "SELECT * FROM users WHERE brukernavn = %s",
            (username,),
        )
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
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/tickets/new", methods=["GET", "POST"])
def new_ticket():
    if "user_id" not in session:
        return redirect(url_for("login"))

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
def my_tickets():
    if "user_id" not in session:
        return redirect(url_for("login"))

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
