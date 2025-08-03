import os
from dotenv import load_dotenv

def load_config(app):
    load_dotenv()
    app.config['UMLS_API_KEY'] = os.getenv("UMLS_API_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
