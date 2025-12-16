import json

from QLCC import db, app
from sqlalchemy import Column, Integer, Float, String, Boolean

class Base(db.Model):
    __abstract__ = True
    def __str__(self):
        return str(self.name)

class Apartment(Base):
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(String(100), nullable=False)
    price = db.Column(Float, nullable=False, default=0)
    acreage = db.Column(Integer, nullable=False)
    capacity = db.Column(Integer, nullable=False)
    image = db.Column(String(1000), default="https://res.cloudinary.com/dy1unykph/image/upload/v1743062897/isbvashxe10kdwc3n1ei.png")
    status = db.Column(String(50), nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        with open("data/apartment.json", encoding="utf-8") as f:
            apartment = json.load(f)
            for a in apartment:
                db.session.add(Apartment(**a))
        db.session.commit()

