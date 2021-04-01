"""Flask app for Cupcakes"""

from flask import Flask, render_template, flash, session, g, redirect
from models import db, connect_db, User
from forms import LoginForm, SignupForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///capstone'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "this-is-secret"

# app.config['SQLALCHEMY_ECHO'] = True
# from flask_debugtoolbar import DebugToolbarExtension
# app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
# debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()
CURR_USER = "curr_user"

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
        return render_template("home.html")

    return render_template("home-anon.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
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

# @app.route('/users/username/posts')
# @app.route('/users/username/followers')
# @app.route('/users/username/following')

##### Helpers #####

def do_login(user):
    """Log in user."""

    session[CURR_USER] = user.username


def do_logout():
    """Logout user."""

    if CURR_USER in session:
        del session[CURR_USER]