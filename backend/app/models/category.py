from beanie import Document

class Category(Document):
    name: str
    icon: str  # Тут зберігається назва іконки або emoji
    color: str

    class Settings:
        name = "categories"
