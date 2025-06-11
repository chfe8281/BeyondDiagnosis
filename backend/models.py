from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import ARRAY

from __init__ import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(225), nullable=False)
    name = db.Column(db.String(100))
    first_login = db.Column(db.Boolean, default = False, nullable = False)
    avatar_url = avatar_url = db.Column(db.Text)
    
    def get_id(self):
        return str(self.user_id) # returns id attribute made by me, as it was not called id.
    
class Profile(db.Model):
    __tablename__ = 'profiles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True, nullable = False)
    bio = db.Column(db.String(200))
    status = db.Column(db.String(50), default = "Patient", nullable=False)
    location = db.Column(db.String(50), nullable=False)
    interests = db.Column(ARRAY(db.Text))
    conditions = db.Column(ARRAY(db.Text))
    avatar_url = db.Column(db.Text)

    def __repr__(self):
        return f'<Profile user_id={self.user_id}, status={self.status}>'
