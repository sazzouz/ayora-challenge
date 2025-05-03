import os

import environ

# Set default values and casting
env = environ.Env(DEBUG=(bool, False))

current_path = environ.Path(__file__) - 1
site_root = current_path - 2
env_file = site_root(".env")

# Determine which env file to load based on DJANGO_ENV
django_env = os.environ.get("DJANGO_ENV", "DEV")
if django_env == "PROD":
    env_file = site_root(".env.prod")
else:
    env_file = site_root(".env")

# Load the appropriate env file if it exists
if os.path.exists(env_file):  # pragma: no cover
    environ.Env.read_env(env_file=env_file)
