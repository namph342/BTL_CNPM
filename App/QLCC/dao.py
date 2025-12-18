import hashlib
import json

from QLCC import app, db
from QLCC.models import Canho, User


def load_apartment_details():
    # with open("data/canho.json", encoding="utf-8") as f:
    #     details = json.load(f)
    #     return details
    return Canho.query.all()

def auth_user(username, password):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    return User.query.filter(User.username==username, User.password==password).first()

def add_user(name, username, password, avatar, email, phonenumber):
    password=hashlib.md5(password.encode("utf-8")).hexdigest()
    u = User(name=name, username=username, password=password, avatar=avatar, email = email, phonenumber = phonenumber)
    db.session.add(u)
    db.session.commit()

def get_user_by_id(id):
    return User.query.get(id)

def load_apartment_by_id(id):
    return Canho.query.get(id)

if __name__ == "__main__":
    with app.app_context():
        print(auth_user("user", "123"))