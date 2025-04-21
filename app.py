
from flask import Flask, render_template, request, redirect, url_for, session
from unfollow_bot_simples import InstagramUnfollowBot
import os
import threading

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "secret")

bot_instance = None
bot_status = {
    "running": False,
    "log": []
}

def log_callback(message):
    bot_status["log"].append(message)
    if len(bot_status["log"]) > 100:
        bot_status["log"] = bot_status["log"][-100:]

def run_bot(username, password):
    global bot_instance
    bot_instance = InstagramUnfollowBot(username, password)
    bot_instance._log = lambda msg, level="INFO": log_callback(f"[{level}] {msg}")
    bot_status["running"] = True
    try:
        bot_instance.run(delay_seconds=10, max_unfollows_per_day=50)
    finally:
        bot_status["running"] = False

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        session["username"] = username
        session["password"] = password
        if not bot_status["running"]:
            thread = threading.Thread(target=run_bot, args=(username, password))
            thread.start()
        return redirect(url_for("status"))
    return render_template("index.html")

@app.route("/status")
def status():
    return render_template("status.html", log=bot_status["log"], running=bot_status["running"])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
