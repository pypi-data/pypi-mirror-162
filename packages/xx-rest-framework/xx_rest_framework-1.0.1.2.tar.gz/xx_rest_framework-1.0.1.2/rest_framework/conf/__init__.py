import os
import json

ROOT_PATH = os.getenv("TORNADO_WORKDIR", os.getcwd())
config = {}
config_path = os.path.join(ROOT_PATH, "config.json")
if os.path.isfile(config_path):
    with open(config_path, "r", encoding="utf8") as fp:
        config = json.load(fp)
__all__ = [
    config
]

if __name__ == '__main__':
    print(config)
    print(ROOT_PATH)
