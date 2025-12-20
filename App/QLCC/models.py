import json

from QLCC import db, app
from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as EnumRole
from flask_login import UserMixin

class Base(db.Model):
    __abstract__ = True
    id= db.Column(Integer, primary_key=True, autoincrement=True)
    def __str__(self):
        return str(self.name)

class Canho(Base):
    name = db.Column(String(100), nullable=False)
    price = db.Column(Float, nullable=False, default=0)
    acreage = db.Column(Integer, nullable=False)
    capacity = db.Column(Integer, nullable=False)
    image = db.Column(String(1000), default="https://res.cloudinary.com/dy1unykph/image/upload/v1743062897/isbvashxe10kdwc3n1ei.png")
    status = db.Column(String(50), nullable=False)
    hopdong = relationship('Hopdong', backref="Canho", lazy=True)

class Hopdong(Base):
    start_date = db.Column(DateTime, nullable=False, default=datetime.now)
    end_date = db.Column(DateTime, nullable=False)
    status = db.Column(String(50), nullable=False)
    client_id = db.Column(Integer, ForeignKey('user.id'), nullable=False)
    room_id = db.Column(Integer, ForeignKey('canho.id'), nullable=False)
    hoadon = relationship('Hoadon', backref="Hopdong", lazy=True)

class UserRole(EnumRole):
    ADMIN = 0
    USER = 1
    SECURITY = 2

class User(Base, UserMixin):
    name = db.Column(String(100), nullable=False)
    phonenumber = db.Column(String(100))
    email = db.Column(String(100))
    username = db.Column(String(100), nullable=False, unique=True)
    password = db.Column(String(100), nullable=False)
    role = db.Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    avatar = db.Column(String(1000),default="https://res.cloudinary.com/dhmt3nfpz/image/upload/v1766058336/default-avatar-profile-icon-social-media-user-photo-in-flat-style-vector_ci4kl9.jpg")
    hopdong = relationship('Hopdong', backref="User", lazy=True)
    suco = relationship('Suco', backref="User", lazy=True)

class Hoadon(Base):
    name = db.Column(String(100), nullable=False)
    created_date = db.Column(DateTime, nullable=False, default=datetime.now)
    payment_status = db.Column(String(50), nullable=False)
    hopdong_id = Column(Integer, ForeignKey('hopdong.id'), nullable=False)
    chitiethoadon = relationship('Chitiethoadon', backref="Hoadon", lazy=True)

class Chitiethoadon(Base):
    name = db.Column(String(100), nullable=False)
    apartment_patment = db.Column(String(100), nullable=False)
    electric_old=db.Column(Integer, nullable=False)
    electric_new=db.Column(Integer, nullable=False)
    water_old=db.Column(Integer, nullable=False)
    water_new=db.Column(Integer, nullable=False)
    electric_fee=db.Column(Integer, nullable=False)
    water_fee=db.Column(Integer, nullable=False)
    Total_fee=db.Column(Integer, nullable=False)
    hoadon_id = Column(Integer, ForeignKey('hoadon.id'), nullable=False)

class Suco(Base):
    name = db.Column(String(100), nullable=False)
    description = db.Column(Text, nullable=False)
    created_date = db.Column(DateTime, nullable=False, default=datetime.now)
    status = db.Column(String(50), nullable=False)
    client_id = db.Column(Integer, ForeignKey('user.id'), nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        with open("data/canho.json", encoding="utf-8") as f:
            apartment = json.load(f)
            for a in apartment:
                db.session.add(Canho(**a))

        import hashlib
        password = hashlib.md5("123".encode('utf-8')).hexdigest()
        u1=User(name="client", username='client', password=password)
        u2 = User(name="management", username='management', password=password, role=UserRole.ADMIN)
        u3 = User(name="security", username='security', password=password, role=UserRole.SECURITY)
        db.session.add_all([u1, u2, u3])
        db.session.commit()

