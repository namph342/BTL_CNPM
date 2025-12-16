import json

from QLCC.models import Apartment


def load_apartment_details():
    # with open("data/apartment.json", encoding="utf-8") as f:
    #     details = json.load(f)
    #     return details
    return Apartment.query.all()