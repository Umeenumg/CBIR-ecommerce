from bson import Binary
import config
from db.mongo import products
from cbir.preprocess import load_image
from cbir.feature_extractor import extract_batch
 
 
def main():
    col = products()
    done = 0
    for doc in col.find({"features": {"$exists": False}}):
        img = load_image(config.IMAGES_DIR / doc["image_path"])
        vec = extract_batch([img])[0]
        blob = Binary(vec.astype("float32").tobytes())
        col.update_one({"_id": doc["_id"]}, {"$set": {"features": blob}})
        done += 1
        print(done, doc["name"])
    print("Termine :", done, "vecteurs")
 
if __name__ == "__main__":
    main()