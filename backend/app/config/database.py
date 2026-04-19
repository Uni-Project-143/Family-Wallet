import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


load_dotenv()

MONGO_URL = os.getenv("MONGO_ATLAS")

db_client = AsyncIOMotorClient(MONGO_URL)
