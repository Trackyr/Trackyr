import os

class Config():
    CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__ + "/../.."))

    ADS_FILE = f"{CURRENT_DIRECTORY}/ads.json"
    SOURCE_MODULES_DIR = "modules/sources"
    NOTIF_AGENT_MODULES_DIR = "modules/notif_agents"

    LOG_PATH = f"{CURRENT_DIRECTORY}/logs"
