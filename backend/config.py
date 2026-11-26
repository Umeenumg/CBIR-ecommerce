import os
from pathlib import Path
from dotenv import load_dotenv
 
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
 
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "cbir_shop")
COLLECTION = "products"
#IMAGES_DIR = BASE_DIR / "static" / "images"
IMAGES_DIR = BASE_DIR.parent / "data" / "raw"
IMAGE_SIZE = (224, 224)
FEATURE_DIM = 1280

MAX_CONTENT_LENGTH = 5 * 1024 * 1024        # 5 Mo
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
TOP_K = 12                                   # nombre max de resultats
SIMILARITY_THRESHOLD = 0.5                   # seuil provisoire (calibre en Day 4