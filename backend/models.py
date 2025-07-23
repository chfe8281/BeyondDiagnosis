from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime, timezone
from sqlalchemy import PrimaryKeyConstraint

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
    status = db.Column(db.String(50), db.CheckConstraint("status IN ('Patient', 'Caregiver')"), default = 'Patient', nullable=False)
    location = db.Column(db.String(50), nullable=False)
    interests = db.Column(ARRAY(db.Text))
    conditions = db.Column(ARRAY(db.Text))
    avatar_url = db.Column(db.Text)
    private = db.Column(db.Boolean, default = True, nullable = False)

    def __repr__(self):
        return f'<Profile user_id={self.user_id}, status={self.status}>'
    
class Friend_Requests(db.Model):
    __tablename__ = 'friend_requests'
    request_id = db.Column(db.Integer, primary_key = True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    requested_at = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    status = db.Column(db.String(20), db.CheckConstraint("status IN ('pending', 'accepted', 'rejected')"), default = 'pending', nullable = False)
    
class Friends(db.Model):
    __tablename__ = 'friends'
    user1_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key = True)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key = True)
    __tableargs__ = (
        db.CheckConstraint(user1_id < user2_id, name = "check_diff_users"),)
    
class Groups(db.Model):
    __tablename__ = 'groups'
    group_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    creator = db.Column(db.String(50), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    avatar_link = db.Column(db.Text)
    description = db.Column(db.String(140), nullable = False)
    
class GroupRequests(db.Model):
    __tablename__ = 'group_requests'
    group_request_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    requested_at = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    status = db.Column(db.String(20), db.CheckConstraint("status IN ('pending', 'accepted', 'rejected')"), default = 'pending', nullable = False)
    
    
class GroupMembers(db.Model):
    __tablename__ = 'groups_to_users'
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    joined_at = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    
    __table_args__ = (
        PrimaryKeyConstraint('group_id', 'user_id'),
    )
    
class Posts(db.Model):
    __tablename__ = 'posts'
    post_id = db.Column(db.Integer, primary_key = True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    content = db.Column(db.String(200), nullable = False)
    time_posted = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    image_url = db.Column(db.Text)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))