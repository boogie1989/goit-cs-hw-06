import os
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from pathlib import Path
from pymongo import MongoClient

ENV_PATH = Path(__file__).parent / ".env"


def create_connect() -> MongoClient:
    load_dotenv(ENV_PATH)
    client = MongoClient(
        os.getenv("MONGO_DB_HOST"),
        server_api=ServerApi("1"),
    )
    return client
