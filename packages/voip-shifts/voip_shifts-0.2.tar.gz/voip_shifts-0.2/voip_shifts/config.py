from redis import Redis
from redis.exceptions import AuthenticationError
from rq import Queue
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

import os
import logging

class Config:

    def __init__(self) -> None: 
        self.SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", 
            "postgresql://postgres:root@127.0.0.1/vp22_backend")
        self.REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
        self.REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "redis")
        self.REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
        self.REDIS_DB = os.environ.get("REDIS_DB", 0)
        self.BOT_KEY = os.environ.get("BOT_KEY")
        assert self.BOT_KEY, "BOT_KEY is not specified"

class ProductionConfig(Config):

    def __init__(self) -> None:
        self.SIP_PASSWORD = os.environ.get("SIP_PASSWORD")
        assert self.SIP_PASSWORD, "SIP_PASSWORD is not specified"
        self.SIP_USERNAME = os.environ.get("SIP_USERNAME")
        assert self.SIP_USERNAME, "SIP_USERNAME is not specified"
        self.SIP_NUMBER = os.environ.get("SIP_NUMBER")
        assert self.SIP_NUMBER, "SIP_NUMBER is not specified"
        self.SIP_SERVER = os.environ.get("SIP_SERVER")
        assert self.SIP_SERVER, "SIP_SERVER is not specified"


log = logging.getLogger()
log.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
fileHandler = logging.FileHandler("./INFO.log")
formatter = logging.Formatter('%(levelname)s:%(asctime)s :: %(message)s', "%Y-%m-%d %H:%M:%S")
streamHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)
log.addHandler(streamHandler)
log.addHandler(fileHandler)


mode = os.environ.get("DEPLOY_MODE", "dev")

if mode == "prod":
    config = ProductionConfig()
else:
    config = Config()

redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, 
              db=config.REDIS_DB, password=config.REDIS_PASSWORD)

rq = Queue("high", connection=redis)
Base = declarative_base()
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
session = Session(engine)
