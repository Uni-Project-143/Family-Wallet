from beanie import Document
from typing import List

class Category(Document):
    name: str
    icon: str
    color: str
    mcc_list: List[int] = []

    class Settings:
        name = "categories"
