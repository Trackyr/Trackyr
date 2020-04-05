import os
import yaml

def _get_defaults():
    s = {}
    s["gobal_include"] = []
    s["gobal_exclude"] = []
    s["recent_ads"] = 3
    s["log_rotation_files"] = 5
    return s

def get_comments():
    return """\
# log_rotation_files: number of files to keep in log rotation
# global_include: a global include that spans across all tasks
# global_exclude: a global exclude that spans across all tasks
# recent_ads: only display the most recent number of ads 
#             to prevent a large notification dump
"""

def load(file):
    global _settings

    _settings = _get_defaults()

    if not os.path.exists(file):
        with open(file, "w") as stream:
            stream.write(get_comments())
            yaml.safe_dump(_settings, stream)

    with open(file, "r") as stream:
        _settings = yaml.safe_load(stream)

def get(key):
    return _settings[key]

if __name__ == "__main__":
    print(load_settings("settings.yaml").__dict__)

