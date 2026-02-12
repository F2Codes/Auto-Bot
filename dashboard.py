from flask import Flask, render_template, request, redirect, session
import json
import sqlite3
import asyncio
from telegram import Bot

CONFIG_FILE = "config.json"
DB_NAME = "users.db"

app = Flask(__name__)
app.secret_key = "supersecretkey"


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


def get_user_count():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count


@app.route("/", methods=["GET", "POST"])
def login():
    config = load_config()

    if request.method == "POST":
        if (
            request.form["username"] == config["DASHBOARD_USERNAME"]
            and request.form["password"] == config["DASHBOARD_PASSWORD"]
        ):
            session["logged_in"] = True
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("logged_in"):
        return redirect("/")

    config = load_config()

    if request.method == "POST":

        # Toggle auto reply
        if "toggle_auto" in request.form:
            config["AUTO_REPLY"] = not config["AUTO_REPLY"]
            save_config(config)

        # Change auto reply message
        if "new_reply" in request.form:
            config["AUTO_REPLY_MESSAGE"] = request.form["new_reply"]
            save_config(config)

        # Broadcast
        if "broadcast" in request.form:
            message = request.form["broadcast"]
            asyncio.run(send_broadcast(message))

    return render_template(
        "dashboard.html",
        users=get_user_count(),
        auto=config["AUTO_REPLY"],
        reply=config["AUTO_REPLY_MESSAGE"]
    )


async def send_broadcast(message):
    config = load_config()
    bot = Bot(config["BOT_TOKEN"])

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    for user in users:
        try:
            await bot.send_message(user[0], message)
        except:
            pass


if __name__ == "__main__":
    app.run(port=5000)
