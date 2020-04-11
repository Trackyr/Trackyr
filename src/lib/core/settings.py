import os
import yaml
import logging

DATA_MODE_YAML = "YAML"
DATA_MODE_DB = "DB"

LOG_MODE_INFO = "INFO"
LOG_MODE_DEBUG = "DEBUG"

def _get_defaults():
    s = {}
    s["global_include"] = []
    s["global_exclude"] = []
    s["recent_ads"] = 0
    s["log_rotation_files"] = 5
    s["log_mode"] = LOG_MODE_INFO
    s["data_mode"] = DATA_MODE_DB
    return s

def get_comments():
    return """\
# log_rotation_files: number of files to keep in log rotation
# global_include: a global include that spans across all tasks
# global_exclude: a global exclude that spans across all tasks
# recent_ads: only display the most recent number of ads 
#             to prevent a large notification dump
"""

def load():
    file = os.path.dirname(os.path.abspath(__file__ + "/../..")) + "/settings.yaml"

    if not os.path.exists(file):
        result = convert(_get_defaults())
        save(file)

    with open(file, "r") as stream:
        raw = yaml.safe_load(stream)

    result = convert(raw)
    return result

def convert(raw):
    default = _get_defaults()
    result = {}

    for key in raw:
        if not key in default:
            raise ValueError(f"Invalid setting: {key}")

        val = raw[key]
        if key == "log_mode":
            result[key] = get_log_mode(val)
        else:
            result[key] = val

    return result

def get_log_mode(mode):
    modes = {
        LOG_MODE_INFO: logging.INFO,
        LOG_MODE_DEBUG: logging.DEBUG
    }

    if not mode in modes:
        raise ValueError(f"Invalid log mode: {mode} choose from {list.modes}")

    return modes[mode]

def save(file):
    if not os.path.exists(file):
        with open(file, "w") as stream:
            stream.write(get_comments())
            yaml.safe_dump(_settings, stream)

def get(key):
    return _settings[key]


_settings = load()
