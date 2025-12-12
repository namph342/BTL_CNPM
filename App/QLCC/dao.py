import json


def load_apartment_details():
    with open('apartment_details.json') as json_file:
        details = json.load(json_file)



        return details