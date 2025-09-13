from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database setup
def init_db():
    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            workout_type TEXT,
            duration INTEGER,
            calories_burned INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Home Page
@app.route("/")
def home():
    return render_template("index.html")

# Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("fitness.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for("login"))
        except:
            return "Username already exists!"
        finally:
            conn.close()
    return render_template("signup.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("fitness.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session["user_id"] = user[0]
            return redirect(url_for("dashboard"))
        return "Invalid credentials!"
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("home"))

# Dashboard
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# Add Workout
@app.route("/add_workout", methods=["GET", "POST"])
def add_workout():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        date = request.form["date"]
        workout_type = request.form["workout_type"]
        duration = request.form["duration"]
        calories = request.form["calories"]
        conn = sqlite3.connect("fitness.db")
        c = conn.cursor()
        c.execute("INSERT INTO workouts (user_id, date, workout_type, duration, calories_burned) VALUES (?, ?, ?, ?, ?)",
                  (session["user_id"], date, workout_type, duration, calories))
        conn.commit()
        conn.close()
        return redirect(url_for("history"))
    return render_template("add_workout.html")

# Workout History
@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()
    c.execute("SELECT date, workout_type, duration, calories_burned FROM workouts WHERE user_id=?", (session["user_id"],))
    workouts = c.fetchall()
    conn.close()
    return render_template("history.html", workouts=workouts)

if __name__ == "__main__":
    app.run(debug=True)
