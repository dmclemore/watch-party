from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, InputRequired


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=8)])


class SignupForm(FlaskForm):
    """Signup form."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[
                             DataRequired(), Length(min=8)])


class NewRoomForm(FlaskForm):
    """New Room form."""

    id = StringField("Room Name", validators=[InputRequired()])
    password = PasswordField("If you want a private room, enter a password")


class RoomForm(FlaskForm):
    """Room Password form."""

    password = PasswordField("Password", validators=[InputRequired()])
