import os
from dotenv import load_dotenv

class AppConfig:
    """
    Manages the application's configuration using environment variables.
    """
    def __init__(self):
        load_dotenv()
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        self.PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
        self.ZYLA_API_KEY = os.getenv("ZYLA_API_KEY")
        self.FILEIO_UPLOAD_URL = "https://file.io/"
        self.ZYLA_OCR_API_URL = "https://zylalabs.com/api/37/optical+character+recognition+api/108/image+analysis"
        self.CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
        self.CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
        self.CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")