# CBIR E-commerce — Recherche de produits par image

Application web e-commerce permettant de rechercher des produits visuellement similaires à partir d'une image.

L'utilisateur téléverse une image depuis le frontend. Le backend extrait ses caractéristiques visuelles, compare son vecteur avec ceux du catalogue et retourne les produits les plus similaires.

**Technologies :** React, Flask, MongoDB, TensorFlow, MobileNetV2.

**Méthode CBIR :**

- Modèle : MobileNetV2 pré-entraîné sur ImageNet (`include_top=False`).
- Extraction : vecteurs de caractéristiques de dimension 1280.
- Similarité : similarité cosinus.
- Recherche : classement des produits par similarité décroissante.
- Filtre textuel facultatif : filtre les produits par nom, marque ou catégorie avant le classement visuel.

## Prérequis

- Python 3.10+
- Node.js 18+
- MongoDB Community ou Docker
- Git

## 1. Cloner le projet

```bash
git clone <url-du-depot>
cd CBIR_ecommerce
```

Créer et activer l'environnement virtuel :

**Windows PowerShell :**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS :**

```bash
python -m venv .venv
source .venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

## 2. Configuration MongoDB

Lancer MongoDB localement ou avec Docker :

```bash
docker run -d --name cbir-mongodb -p 27017:27017 mongo:7
```

Configurer les variables d'environnement dans `backend/.env` à partir de `backend/.env.example`.

Paramètres principaux :

- `MONGO_URI` : URI de connexion MongoDB.
- `DB_NAME` : nom de la base de données.
- `SIMILARITY_THRESHOLD` : seuil minimal de similarité.

Ne jamais versionner le fichier `.env`.

## 3. Préparer le catalogue

Le catalogue contient des images organisées par catégorie dans :

```text
data/raw/<category>/
```

Les métadonnées des produits sont dans :

- `data/products.csv` : informations sur les produits.
- `data/image_sources.csv` : correspondance entre les images et leurs sources.
- `evaluation/annotations.csv` : catégories attendues pour les images de test.

Depuis le dossier `backend/` :

```bash
python -m scripts.load_catalog
python -m scripts.compute_features
```

Ces commandes permettent de :

1. Importer les produits du fichier CSV dans MongoDB.
2. Extraire les caractéristiques visuelles avec MobileNetV2.
3. Enregistrer les vecteurs de caractéristiques dans MongoDB.

**Remarque :** le calcul des vecteurs est nécessaire lors de la première préparation du catalogue. Le modèle MobileNetV2 peut télécharger ses poids ImageNet lors de son premier chargement.

## 4. Lancer l'application

**Backend — depuis `backend/` :**

```bash
python app.py
```

API disponible à :

```text
http://127.0.0.1:5000
```

Vérification :

```text
http://127.0.0.1:5000/api/health
```

**Frontend — depuis `frontend/` :**

```bash
npm install
npm run dev
```

Ouvrir l'adresse locale affichée par Vite dans le terminal.

## 5. Architecture du projet

```text
CBIR_ecommerce/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── cbir/
│   │   ├── preprocess.py
│   │   ├── feature_extractor.py
│   │   ├── similarity.py
│   │   └── index.py
│   ├── db/
│   │   ├── mongo.py
│   │   └── repository.py
│   ├── routes/
│   │   ├── products.py
│   │   └── search.py
│   └── scripts/
│       ├── load_catalog.py
│       └── compute_features.py
├── data/
│   ├── raw/
│   ├── products.csv
│   └── image_sources.csv
├── evaluation/
│   ├── test_images/
│   ├── hors_catalogue/
│   ├── annotations.csv
│   ├── eval_precision.py
│   ├── calibrate_threshold.py
│   ├── compare_models.py
│   └── metrics.py
└── frontend/
```

## 6. API REST

| Méthode | Endpoint                        | Description                       |
| ------- | ------------------------------- | --------------------------------- |
| GET     | `/api/products/random?limit=12` | Récupérer des produits aléatoires |
| GET     | `/api/products?category=&q=`    | Filtrer les produits              |
| GET     | `/api/products/<id>`            | Récupérer un produit              |
| POST    | `/api/search`                   | Recherche visuelle par image      |

**Recherche par image :**

Endpoint : `POST /api/search`

Format : `multipart/form-data`

Paramètres :

- `image` : image obligatoire (JPG, JPEG, PNG ou WEBP).
- `q` : texte facultatif pour filtrer les produits.

## 7. Évaluation

Les scripts d'évaluation permettent de mesurer les performances du système.

Depuis la racine du projet :

```bash
python evaluation/eval_precision.py
python evaluation/calibrate_threshold.py
```

Métriques utilisées :

- Top-1 Accuracy
- Precision@5
- Precision@10
- Analyse des erreurs de classement

Les résultats sont enregistrés dans `evaluation/results/`.

Le script de calibration permet d'étudier le seuil de similarité à partir des images pertinentes et hors catalogue.

## 8. Sources

- Dataset d'images : Fashion Product Images Dataset (Kaggle).
- Modèle : MobileNetV2 pré-entraîné sur ImageNet.
- Sources et identifiants des images : `data/image_sources.csv`.
