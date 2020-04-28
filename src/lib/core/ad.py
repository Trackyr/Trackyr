import os
import yaml
import json

import lib.utils.logger as log
from lib.core.config import Config

def save():
    from lib.core.state import State

    ads = State.get_ads()
    file = Config.ADS_FILE

    with open(file, "w") as stream:
        json.dump(ads, stream)

def load():
    from lib.core.state import State

    file = Config.ADS_FILE

    if not os.path.exists(file):
        with open(file, "w") as stream:
            stream.write("{}")

    with open(file, "r") as stream:
        ads = yaml.safe_load(stream)

    for key in ads:
        log.debug(f"Total old ads from {key}: {len(ads[key])}")

    return ads
