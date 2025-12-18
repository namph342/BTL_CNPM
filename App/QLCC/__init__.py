from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)

app.secret_key="aksdh uwhdhdiuawd7w83h7x8yq38ryj"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/aptdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

cloudinary.config(cloud_name='dhmt3nfpz',
                  api_key='126381671171798',
                  api_secret='eVE0ooPsZFZGvDUjHi6y3TbKl70')

db = SQLAlchemy(app)
login_manager = LoginManager(app)


