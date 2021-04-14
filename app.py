"""Flask app for Cupcakes"""

from flask import Flask, render_template, flash, session, g, redirect, jsonify, request
from models import db, connect_db, User
from forms import LoginForm, SignupForm
from sqlalchemy.exc import IntegrityError
from flask_socketio import SocketIO
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", "postgresql:///capstone")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "this-is-secret")
connect_db(app)
socketio = SocketIO(app)

# app.config['SQLALCHEMY_ECHO'] = True
# from flask_debugtoolbar import DebugToolbarExtension
# app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
# debug = DebugToolbarExtension(app)

CURR_USER = "curr_user"

if __name__ == "__main__":
    socketio.run(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER in session:
        g.user = User.query.get(session[CURR_USER])

    else:
        g.user = None


@app.route("/")
def home():

    if g.user:
        return render_template("home.html", user=g.user)

    return render_template("home-anon.html")


@app.route("/room/<room_id>")
def room(room_id):

    if g.user:
        return render_template("room.html", user=g.user, roomId=room_id)

    return render_template("home-anon.html")

# @app.route("/messages")
# def messages():


############### LOGIN/LOGOUT/SIGNUP ###############


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Goodbye!", "success")
    return redirect("/")


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user login."""

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(form.username.data,
                               form.password.data,
                               form.first_name.data,
                               form.last_name.data)
            db.session.commit()
            do_login(user)
            flash(f"Welcome to WatchParty!", "success")
            return redirect("/")

        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("users/signup.html", form=form)

    return render_template("users/signup.html", form=form)


############### SOCKET EVENTS ###############


@socketio.on('connect')
def handle_connection():
    socketio.emit("renderMessage", {
        "username": "[SYSTEM]",
        "message": f"{session[CURR_USER]} has connected."
    })


@socketio.on('disconnect')
def handle_disconnection():
    socketio.emit("renderMessage", {
        "username": "[SYSTEM]",
        "message": f"{session[CURR_USER]} has disconnected."
    })


@socketio.on('send_chat')
def handle_send_chat(json, methods=["GET", "POST"]):
    socketio.emit("renderMessage",
                  json, callback=message_received)


############### HELPERS ###############


def do_login(user):
    """Log in user."""

    session[CURR_USER] = user.username


def do_logout():
    """Logout user."""

    if CURR_USER in session:
        del session[CURR_USER]


def message_received(methods=["GET", "POST"]):
    print("[MESSAGE RECIEVED]")
