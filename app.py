from flask import Flask, render_template, flash, session, g, redirect, jsonify, request
from models import db, connect_db, User, Room
from forms import LoginForm, SignupForm, NewRoomForm, RoomForm
from sqlalchemy.exc import IntegrityError
from flask_socketio import SocketIO, join_room, leave_room
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
CURR_ROOM = "curr_room"

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
    """If we're logged in, show the home page with a list of all chat rooms."""

    if not g.user:
        return render_template("home-anon.html")

    rooms = Room.query.all()

    return render_template("home.html", user=g.user, rooms=rooms)


@app.route("/room/new", methods=["GET", "POST"])
def new_room():
    """Show the new room form. On submit, create and go to the new room."""

    # If no one is logged in, show the anon home page.
    if not g.user:
        return render_template("home-anon.html")

    form = NewRoomForm()

    # If conditional will return true when the form submits a response
    if form.validate_on_submit():
        try:
            if form.password.data:
                room = Room.create(
                    id=form.id.data,
                    owner=g.user.username,
                    password=form.password.data,
                    is_private=True,
                )
            else:
                room = Room.create(
                    id=form.id.data,
                    owner=g.user.username
                )
            db.session.commit()
            return redirect(f"/room/{room.id}")

        except IntegrityError:
            flash("Room Name already taken", "danger")
            return render_template("/room/new-room.html", form=form)

        except:
            flash("Something went wrong. Try again!", "danger")
            return render_template("/room/new-room.html", form=form)

    return render_template("/room/new-room.html", form=form)


@app.route("/room/<room_id>")
def room(room_id):
    """Show the room with name of room_id."""

    if not g.user:
        return render_template("home-anon.html")

    room = Room.query.filter_by(id=f"{room_id}").first()

    return render_template("/room/room.html", user=g.user, roomId=room_id, room=room)


@app.route("/room/<room_id>/password", methods=["GET", "POST"])
def room_password(room_id):
    """Show the password form. Authenticate the password for the room with id of room_id."""

    # If no one is logged in, show the anon home page.
    if not g.user:
        return render_template("home-anon.html")

    form = RoomForm()

    # If conditional will return true when the form submits a response
    if form.validate_on_submit():
        room = Room.authenticate(id=room_id, password=form.password.data)
        if room:
            return redirect(f"/room/{room.id}")

        flash("Invalid credentials.", 'danger')

    return render_template("/room/password.html", form=form)

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
                               form.password.data)
            db.session.commit()
            do_login(user)
            flash(f"Welcome to WatchParty!", "success")
            return redirect("/")

        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("users/signup.html", form=form)

    return render_template("users/signup.html", form=form)


############### API ROUTES ###############


@app.route('/api/<room_id>/current')
def get_current_video(room_id):
    """Get the rooms current video."""

    current_video = Room.query.filter_by(id=f"{room_id}").first().current_video
    return jsonify(current_video=current_video)


@app.route("/api/<room_id>/current", methods=["POST"])
def set_current_video(room_id):
    """Set the rooms current video."""

    video = request.json["video"]
    room = Room.query.filter_by(id=f"{room_id}").first()
    room.current_video = video
    db.session.commit()
    return (jsonify(current_video=room.current_video), 201)

############### SOCKET EVENTS ###############


@socketio.on("join")
def handle_room_join(data):
    session[CURR_ROOM] = data["room"]
    join_room(session[CURR_ROOM])

    room = Room.query.filter_by(id=session[CURR_ROOM]).first()
    room.population += 1
    db.session.commit()

    socketio.emit("renderMessage", {
        "username": "[SYSTEM]",
        "message": f'{session[CURR_USER]} has connected.'
    }, to=session[CURR_ROOM])


@socketio.on("disconnect")
def handle_disconnection():
    """Handle the socket disconnection event."""

    # Emit a disconnection message to the user's current room chat.
    socketio.emit("renderMessage", {
        "username": "[SYSTEM]",
        "message": f"{session[CURR_USER]} has disconnected."
    }, to=session[CURR_ROOM])

    # Change the room's population in the database.
    room = Room.query.filter_by(id=session[CURR_ROOM]).first()
    room.population -= 1
    if room.population == 0 and room.id != "general":
        db.session.delete(room)
    db.session.commit()

    # Remove the socket from the room, and remove the room from the session.
    leave_room(session[CURR_ROOM])
    if CURR_ROOM in session:
        del session[CURR_ROOM]


@socketio.on("send_chat")
def handle_send_chat(data):
    """Handle the socket send_chat event."""

    # Call the client-side renderMessage socket event. Will relay the message data.
    socketio.emit("renderMessage", data, to=session[CURR_ROOM])


@socketio.on("next_video")
def handle_next_video(data):
    room = Room.query.filter_by(id=session[CURR_ROOM]).first()
    room.current_video = data["id"]
    db.session.commit()
    socketio.emit("nextVideo", data, to=session[CURR_ROOM])


@socketio.on("play_video")
def handle_play_video():
    socketio.emit("playVideo", to=session[CURR_ROOM])


@socketio.on("stop_video")
def handle_stop_video():
    socketio.emit("stopVideo", to=session[CURR_ROOM])


@socketio.on("sync_video")
def handle_sync_video(data):
    socketio.emit("syncVideo", data, to=session[CURR_ROOM])


############### HELPERS ###############


def do_login(user):
    """Log in user."""

    # Add user to session
    session[CURR_USER] = user.username


def do_logout():
    """Logout user."""

    # Remove user from session
    if CURR_USER in session:
        del session[CURR_USER]
