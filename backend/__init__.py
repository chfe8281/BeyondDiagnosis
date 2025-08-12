from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet


load_dotenv()

fernet_key = os.getenv('FERNET_KEY')
f = Fernet(fernet_key)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
print("🔌 Connected to DB:", app.config['DATABASE_URL'])
db = SQLAlchemy(app)
__all__ = ["app", "db", "f"]