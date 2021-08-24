# WatchParty

WatchParty is a live chat room app where users can watch YouTube videos together in sync. When one user pauses, everyone will pause. If one person rewinds, everyone else will too.

## Motivation

Growing up, I always found myself in come kind of a voice chat with friends. We would often have times where we would take a break from whatever we were doing, and have a snack or just take a breather. Those idle times were often filled with various YouTube videos. But we never really had ways to watch videos together. Modern tech like screen-sharing has since somewhat solved this problem, but I've still always felt there is space for this kind of platform.

## Tech Stack

Python, Flask, Postgres, SQLAlchemy, Javascript, SocketIO, Axios, BCrypt, WTForms, HTML, CSS

## API Reference

Youtube iFrame API - https://developers.google.com/youtube/iframe_api_reference

## To run locally:
### Local dependencies: Python & Postgres

1. Initialize a new virtual environment in the working directory.
   1. `python -m venv venv`
   2. `source venv/bin/activate`
2. Install contents of requirements.txt.
   1. `pip install -r requirements.txt`
3. Create and seed database.
   1. `createdb watchparty`
   2. `python seed.py`
4. Start application
   1. `flask run`
5. Open your browser and go to "http://127.0.0.1:5000/"

## Notes

- There are two test users you can use for demo purposes. Usernames: "admin" & "mod". Both passwords are "password".
- I recommend running this app in one normal browser, and one incognito browser, side by side as different users to see the full functionality.
