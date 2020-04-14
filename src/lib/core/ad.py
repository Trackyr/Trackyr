import os
import lib.utils.logger as log

import yaml
import json

def save(ads, file):
    with open(file, "w") as stream:
        json.dump(ads, stream)

def load(file):
    if not os.path.exists(file):
        with open(file, "w") as stream:
            stream.write("{}")

    with open(file, "r") as stream:
        ads = yaml.safe_load(stream)

    for key in ads:
        log.debug(f"Total old ads from {key}: {len(ads[key])}")

    return ads
