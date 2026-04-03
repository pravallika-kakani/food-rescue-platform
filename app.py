import os
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# On Render the working directory is read-only except /tmp.
# Locally, food.db sits next to app.py (same as before).
DB_PATH = os.environ.get("DB_PATH", "food.db")

MEALS_SAVED = 0


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS food(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor TEXT,
        food_item TEXT,
        quantity TEXT,
        location TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS volunteers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        points INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── PAGES ──────────────────────────────────────────────

@app.route("/")
def dashboard():
    global MEALS_SAVED
    conn = get_db()
    foods      = conn.execute("SELECT * FROM food").fetchall()
    volunteers = conn.execute("SELECT * FROM volunteers ORDER BY points DESC").fetchall()
    conn.close()
    return render_template("dashboard.html",
                           foods=foods, volunteers=volunteers, meals=MEALS_SAVED)


@app.route("/donate")
def donate_page():
    return render_template("donate.html")


@app.route("/claim-food")
def claim_page():
    conn = get_db()
    foods      = conn.execute("SELECT * FROM food").fetchall()
    volunteers = conn.execute("SELECT * FROM volunteers ORDER BY points DESC").fetchall()
    conn.close()
    return render_template("claim.html", foods=foods, volunteers=volunteers)


@app.route("/volunteers")
def volunteers_page():
    conn = get_db()
    volunteers = conn.execute("SELECT * FROM volunteers ORDER BY points DESC").fetchall()
    conn.close()
    return render_template("volunteers.html", volunteers=volunteers)


@app.route("/rewards")
def rewards_page():
    conn = get_db()
    volunteers = conn.execute("SELECT * FROM volunteers ORDER BY points DESC").fetchall()
    conn.close()
    return render_template("rewards.html", volunteers=volunteers)


# ── ACTIONS ────────────────────────────────────────────

@app.route("/add_food", methods=["POST"])
def add_food():
    donor     = request.form["donor"]
    food_item = request.form["food_item"]
    quantity  = request.form["quantity"]
    location  = request.form["location"]

    conn = get_db()
    conn.execute(
        "INSERT INTO food (donor, food_item, quantity, location) VALUES (?,?,?,?)",
        (donor, food_item, quantity, location)
    )
    conn.commit()
    conn.close()
    return redirect("/donate?donated=1")


@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    conn = get_db()
    conn.execute("INSERT INTO volunteers (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return redirect("/volunteers?registered=1")


@app.route("/claim", methods=["POST"])
def claim():
    global MEALS_SAVED
    food_id      = request.form["food_id"]
    volunteer_id = request.form["volunteer_id"]

    conn = get_db()
    conn.execute("DELETE FROM food WHERE id=?", (food_id,))
    conn.execute(
        "UPDATE volunteers SET points = points + 10 WHERE id=?", (volunteer_id,)
    )
    conn.commit()
    conn.close()
    MEALS_SAVED += 1
    return redirect("/claim-food?claimed=1")


@app.route("/redeem/<vol_id>")
def redeem(vol_id):
    conn = get_db()
    row = conn.execute("SELECT points FROM volunteers WHERE id=?", (vol_id,)).fetchone()

    if row and row["points"] >= 50:
        new_pts = row["points"] - 50
        if new_pts == 0:
            conn.execute("DELETE FROM volunteers WHERE id=?", (vol_id,))
        else:
            conn.execute(
                "UPDATE volunteers SET points = ? WHERE id=?", (new_pts, vol_id)
            )
        conn.commit()

    conn.close()
    return redirect("/rewards?redeemed=1")


# ── STARTUP ────────────────────────────────────────────

init_db()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
