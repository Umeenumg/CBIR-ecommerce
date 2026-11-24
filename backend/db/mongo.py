from pymongo import MongoClient
import config
 
_client = None
 
 
def get_db():
    global _client
    if _client is None:
        _client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=3000)
    return _client[config.DB_NAME]
 
 
def products():
    return get_db()[config.COLLECTION]