
from db.mongo import products

col = products()

total = col.count_documents({})
with_features = col.count_documents({
    "features": {"$exists": True}
})
without_features = col.count_documents({
    "features": {"$exists": False}
})

print("Total products:", total)
print("Products with features:", with_features)
print("Products without features:", without_features)

# Inspecter un seul vecteur
doc = col.find_one({"features": {"$exists": True}})

if doc:
    print("Product:", doc["name"])
    print("Category:", doc["category"])
    print("Feature bytes:", len(doc["features"]))
