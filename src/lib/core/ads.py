import json

def save(ads):
    with open(ads_file, "w") as stream:
        json.dump(ads, stream)
