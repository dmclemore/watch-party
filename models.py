from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()
DEFAULT_IMAGE_URL = "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png"

def connect_db(app):
    """Connect the database to the given Flask app"""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model"""

    __tablename__ = "users"

    username = db.Column(
        db.String(20),
        primary_key = True
    )

    password = db.Column(
        db.Text,
        nullable=False
    )
    
    first_name = db.Column(
        db.Text,
        nullable = False
    )

    last_name = db.Column(
        db.Text,
        nullable = False
    )

    image_url = db.Column(
        db.Text,
        nullable = False,
        default = DEFAULT_IMAGE_URL
    )

    # chat_messages = db.relationship(
    #     "Chat_Message",
    #     backref = "user",
    #     cascade="all, delete-orphan"
    # )

    def __repr__(self):
        """Return a clear representation of the user"""

        return self.full_name

    @property
    def full_name(self):
        """Returns the user's full name"""
        
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def signup(cls, username, password, first_name, last_name):
        """Sign up user. Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Check for valid username & password combo"""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

# class Chat_Message(db.Model):

#     __tablename__ = "chat_messages"

#     id = db.Column(
#         db.Integer,
#         primary_key=True,
#         autoincrement=True
#     )

#     message = db.Column(
#         db.Text,
#         nullable=False
#     )

#     username = db.Column(
#         db.Text,
#         db.ForeignKey("users.username"),
#         nullable = False
#     )

#     def serialize(self):

#         return {
#             "username": self.username,
#             "message": self.message
#         }