from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from __init__ import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(225), nullable=False)
    name = db.Column(db.String(100))
    first_login = db.Column(db.Boolean, default = False, nullable = False)
    
    def get_id(self):
        return str(self.user_id) # returns id attribute made by me, as it was not called id.
