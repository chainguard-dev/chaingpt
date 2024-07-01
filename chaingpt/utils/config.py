# Standard lib
from typing import Dict

# 3rd party
import os
from pathlib import Path
import yaml


# TODO: Add checks to config to ensure expected fields are present
CONFIG_FILE_NAME = os.path.join(Path.home(), ".chaingpt", "config.yaml")


def _load_config() -> Dict:
    """
    Searches for a file called config.yaml in the current working
    directory and loads its contents.
    """
    try:
        with open(CONFIG_FILE_NAME, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Missing configuration file. Did you run generate_config.py?")
        exit(-1)


config = _load_config()