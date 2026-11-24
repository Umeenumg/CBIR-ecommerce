import os
from pathlib import Path
from dotenv import load_dotenv
 
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
 
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "cbir_shop")
COLLECTION = "products"
IMAGES_DIR = BASE_DIR / "static" / "images"
IMAGE_SIZE = (224, 224)
FEATURE_DIM = 1280