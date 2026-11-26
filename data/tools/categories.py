"""Configuration du catalogue : 8 categories, 5 familles (electronique, mode, beaute, jouets, maison).
Pour changer de categories, modifie ce fichier (rien d'autre)."""

CATEGORIES = {
    # cle (= nom de dossier = champ "category" dans Mongo) : parametres
    "camera": {
        "label": "Appareil photo",
        "queries": ["digital camera", "mirrorless camera", "dslr camera"],
        "brands": ["Acme", "Nova", "Orion"], "price": (150, 1800),
    },
    "laptop": {
        "label": "Ordinateur portable",
        "queries": ["laptop computer", "notebook laptop desk", "silver laptop"],
        "brands": ["Acme", "Nova", "Orion"], "price": (300, 2200),
    },
    "headphones": {
        "label": "Casque audio",
        "queries": ["headphones", "wireless headphones", "over ear headphones"],
        "brands": ["Acme", "Nova", "Orion"], "price": (25, 350),
    },
    "sneakers": {
        "label": "Baskets",
        "queries": ["sneakers", "running shoes", "white sneakers"],
        "brands": ["Stride", "Nova", "Orion"], "price": (30, 220),
    },
    "handbag": {
        "label": "Sac a main",
        "queries": ["handbag", "leather bag", "women bag"],
        "brands": ["Maison", "Nova", "Orion"], "price": (25, 400),
    },
    "perfume": {
        "label": "Parfum",
        "queries": ["perfume bottle", "fragrance bottle", "cosmetics perfume"],
        "brands": ["Maison", "Aura", "Orion"], "price": (15, 180),
    },
    "teddy_bear": {
        "label": "Peluche",
        "queries": ["teddy bear", "plush toy", "stuffed animal"],
        "brands": ["Joy", "Nova", "Orion"], "price": (8, 60),
    },
    "armchair": {
        "label": "Fauteuil",
        "queries": ["armchair", "sofa chair", "living room chair"],
        "brands": ["Casa", "Nova", "Orion"], "price": (80, 900),
    },
}


def config_for(cat):
    """Config d'une categorie : celle de CATEGORIES si elle existe, sinon une config par defaut
    (cas des categories qui viennent d'un dataset)."""
    if cat in CATEGORIES:
        return CATEGORIES[cat]
    return {"label": cat.replace("_", " ").capitalize(), "queries": [],
            "brands": ["Acme", "Nova", "Orion"], "price": (10, 500)}



# --- Categories importees depuis Kaggle (Fashion Product Images) : libelles et prix realistes ---
def _c(label, lo, hi, brands=("Acme", "Nova", "Orion")):
    return {"label": label, "queries": [], "brands": list(brands), "price": (lo, hi)}


CATEGORIES.update({
    "backpacks": _c("Sac a dos", 20, 120),
    "belts": _c("Ceinture", 10, 80),
    "briefs": _c("Slip", 5, 30),
    "casual_shoes": _c("Chaussures casual", 30, 150),
    "flip_flops": _c("Tongs", 5, 40),
    "formal_shoes": _c("Chaussures de ville", 40, 220),
    "handbags": _c("Sac a main", 25, 300),
    "heels": _c("Talons", 25, 200),
    "jeans": _c("Jean", 25, 120),
    "kurtas": _c("Kurta", 15, 90),
    "perfume_and_body_mist": _c("Parfum", 12, 150),
    "sandals": _c("Sandales", 12, 80),
    "shirts": _c("Chemise", 15, 90),
    "socks": _c("Chaussettes", 3, 20),
    "sports_shoes": _c("Chaussures de sport", 35, 200),
    "sunglasses": _c("Lunettes de soleil", 15, 180),
    "tops": _c("Haut", 10, 70),
    "tshirts": _c("T-shirt", 8, 50),
    "wallets": _c("Portefeuille", 10, 90),
    "watches": _c("Montre", 20, 400),
})