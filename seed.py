from models import db, User
from app import app

# Create tables
db.drop_all()
db.create_all()

# Empty tables, just in case
User.query.delete()

# Default User values
user1 = User.signup(username="Scooby", password="password", first_name="Desmond", last_name="McLemore")
user2 = User.signup(username="Astro", password="password", first_name="Justin", last_name="Ludington")

for u in (user1, user2):
    db.session.add(u)

db.session.commit()