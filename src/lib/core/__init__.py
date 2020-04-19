import yaml
import sys
import lib.core.settings as settings
from lib.core.config import Config

import lib.utils.logger as log
log.load(Config.LOG_PATH, settings.get("log_rotation_files"))

