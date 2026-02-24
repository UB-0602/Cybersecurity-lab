# ================================
# IMPORTS
# ================================

import tensorflow as tf
load_model = tf.keras.models.load_model

from flask import Flask, render_template, request, redirect, session
import numpy as np
import sqlite3
import secrets
import joblib
from collections import defaultdict

from modules.logger import log_event, fetch_logs
from modules.auth import create_token, verify
from modules.password_tools import strength, crack_time


# ================================
# APP SETUP
# ================================

app = Flask(__name__)
app.secret_key = "key"

blocked_ips = set()
activity = defaultdict(int)


# ================================
# LOAD AI MODEL
# ================================

deep_model = load_model("ai/deep_model.h5")
vectorizer = joblib.load("ai/vectorizer.pkl")


# ================================
# GLOBAL BEHAVIOR TRACKING
# ================================

@app.before_request
def track_behavior():
    ip = request.remote_addr

    if ip in blocked_ips:
        return "🚫 Your IP is blocked by Admin"

    activity[ip] += 1
    log_event(f"IP Activity: {ip}")


# ================================
# ATTACK DETECTION
# ================================

def detect_attack(text):

    X = vectorizer.transform([text]).toarray()
    preds = deep_model.predict(X)

    pred = np.argmax(preds)

    labels = ["Normal", "SQL Injection", "XSS Attack"]
    confidence = round(float(np.max(preds)) * 100, 2)

    return labels[pred], confidence


# ================================
# HOME
# ================================

@app.route("/")
def home():
    return render_template("index.html")


# ================================
# WORLD MAP
# ================================

@app.route("/map")
def worldmap():
    return render_template("map.html")


# ================================
# CSRF DEMO
# ================================

@app.route("/csrf", methods=["GET", "POST"])
def csrf():

    token = secrets.token_hex(16)
    session["csrf"] = token

    msg = ""

    if request.method == "POST":
        if request.form.get("token") != session.get("csrf"):
            msg = "⚠ CSRF Attack Detected"
            log_event("CSRF Attack")
        else:
            msg = "Safe Request"

    return render_template("csrf.html", token=token, msg=msg)


# ================================
# AUTH SYSTEM
# ================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        u = request.form["u"]
        p = request.form["p"]

        conn = sqlite3.connect("database.db")
        conn.execute("INSERT INTO users VALUES(NULL,?,?,?)", (u, p, "user"))
        conn.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        u = request.form["u"]
        p = request.form["p"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        r = c.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (u, p)
        ).fetchone()

        if r:
            token = create_token(u, r[0])
            session["token"] = token
            session["role"] = r[0]

            log_event("User login")
            return redirect("/")

    return render_template("login.html")


# ================================
# ADMIN PANEL
# ================================

@app.route("/admin")
def admin():

    try:
        data = verify(session.get("token"))

        if data["role"] != "admin":
            return "Unauthorized"

    except:
        return "Login Required"

    logs = fetch_logs()

    return render_template(
        "admin.html",
        logs=logs,
        blocked=blocked_ips
    )


@app.route("/block/<ip>")
def block(ip):
    blocked_ips.add(ip)
    log_event("Admin blocked IP " + ip)
    return redirect("/admin")


@app.route("/clearlogs")
def clearlogs():
    conn = sqlite3.connect("database.db")
    conn.execute("DELETE FROM logs")
    conn.commit()
    return redirect("/admin")


# ================================
# ANALYTICS DASHBOARD
# ================================

@app.route("/analytics")
def analytics():
    logs = fetch_logs()
    return render_template("analytics.html", logs=logs)


@app.route("/analytics_data")
def analytics_data():

    logs = fetch_logs()

    stats = {"XSS": 0, "SQL": 0, "Normal": 0}

    for l in logs:
        if "XSS" in l:
            stats["XSS"] += 1
        elif "SQL" in l:
            stats["SQL"] += 1
        else:
            stats["Normal"] += 1

    return stats


@app.route("/timeline_data")
def timeline_data():

    logs = fetch_logs()
    timeline = {}

    for i, l in enumerate(logs):
        timeline[i] = 1

    return timeline


# ================================
# PASSWORD TOOL
# ================================

@app.route("/password", methods=["GET", "POST"])
def password():

    s = None
    t = None

    if request.method == "POST":
        pw = request.form["pw"]
        s = strength(pw)
        t = crack_time(pw)
        log_event("Password tested")

    return render_template("password.html", s=s, t=t)


# ================================
# XSS MODULE
# ================================

@app.route("/xss", methods=["GET", "POST"])
def xss():

    text = ""
    result = ""
    conf = 0

    if request.method == "POST":
        text = request.form["t"]

        result, conf = detect_attack(text)
        log_event(f"AI:{result} ({conf}%)")

        # Continuous learning data
        if result != "Normal":
            with open("ai/new_data.txt", "a") as f:
                f.write(text + "\n")

    return render_template("xss.html", text=text, result=result, conf=conf)


# ================================
# SQL INJECTION DEMO (INTENTIONAL)
# ================================

@app.route("/sql_vuln", methods=["GET", "POST"])
def sql_vuln():

    msg = ""

    if request.method == "POST":
        u = request.form["u"]
        p = request.form["p"]

        conn = sqlite3.connect("database.db")

        # INTENTIONALLY VULNERABLE QUERY
        q = f"SELECT * FROM users WHERE username='{u}' AND password='{p}'"
        r = conn.execute(q).fetchone()

        msg = "Access" if r else "Denied"
        log_event("SQL attempt")

    return render_template("sql_vuln.html", msg=msg)


# ================================
# RUN SERVER
# ================================

if __name__ == "__main__":
    app.run(debug=True)