import os
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

REDIS_URL = config.get("database", "url")
WEBSOCKET_URL = config.get("websocket", "url")

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    SECRET_KEY = os.getenv('SECRET_KEY')
