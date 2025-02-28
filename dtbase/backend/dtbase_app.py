from os import environ
from sys import exit

from flask_migrate import Migrate

from dtbase.backend.api import create_app, db
from dtbase.backend.config import config_dict

get_config_mode = environ.get("DT_CONFIG_MODE", "Production")
print(f"get_config_mode is {get_config_mode}")

try:
    config_mode = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit("Error: Invalid DT_CONFIG_MODE environment variable entry.")

app = create_app(config_mode)
Migrate(app, db)
