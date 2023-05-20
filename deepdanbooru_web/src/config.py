import json

config = {}
with open("data/config.json", "r") as f:
    config = json.load(f)

USERNAME = config["username"]
PASSWORD = config["password"]
