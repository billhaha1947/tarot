import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
DB_URI = "sqlite:///" + os.path.join(basedir, "tarot.db")
engine = create_engine(DB_URI, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

db = SQLAlchemy()

def init_db(app=None):
    if app:
        app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(app)
        with app.app_context():
            db.create_all()
    else:
        from flask import Flask
        temp_app = Flask(__name__)
        temp_app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
        temp_app.config["SQLALCHEMY_TRACK_MOD_MODIFICATIONS"] = False
        db.init_app(temp_app)
        with temp_app.app_context():
            db.create_all()
