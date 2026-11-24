import csv
import config
from db.mongo import products
 
CSV_PATH = config.BASE_DIR.parent / "data" / "products.csv"
 
 
def main():
    col = products()
    docs = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            docs.append({
                "name": row["name"],
                "category": row["category"],
                "brand": row["brand"],
                "price": float(row["price"]),
                "description": row["description"],
                "image_path": row["image_file"],
            })
        col.delete_many({})
        col.insert_many(docs)
    print(len(docs), "produits inseres")
 
 
if __name__ == "__main__":
    main()