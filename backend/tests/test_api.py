"""Tests API (mongomock + faux extracteur : sans Mongo ni TensorFlow)."""
import io
 
import mongomock
import numpy as np
import pytest
from bson import Binary
from PIL import Image
 
 
def vec(*vals):
   out = np.zeros(1280, dtype="float32")
   out[: len(vals)] = vals
   return out / np.linalg.norm(out)
def png_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), "red").save(buf, format="PNG")
    return buf.getvalue()
@pytest.fixture
def make_client(monkeypatch):
    def _make(items):
        import cbir.index as index_mod
        import db.mongo as mongo_mod
        from app import create_app
        fake_db = mongomock.MongoClient()["test"]
        monkeypatch.setattr(mongo_mod, "get_db", lambda: fake_db)
        monkeypatch.setattr(index_mod, "_matrix", None)
        monkeypatch.setattr("routes.search.extract_batch", lambda imgs: np.stack([vec(1, 0)]))
        for name, cat, v in items:
            fake_db["products"].insert_one(
                {"name": name, "category": cat, "brand": "X", "price": 10.0,
                 "image_path": f"{name}.jpg", "features": Binary(v.tobytes())})
        return create_app().test_client()
    return _make
CATALOG = [("cam1", "camera", vec(1, 0)), ("cam2", "camera", vec(1, 0.5)),
           ("shoe", "chaussure", vec(0, 0, 1))]
def upload(client, data, filename):
    return client.post("/api/search", data={"image": (io.BytesIO(data), filename)},
                       content_type="multipart/form-data")
def test_health(make_client):
    assert make_client(CATALOG).get("/api/health").get_json() == {"status": "ok"}
def test_sans_image_400(make_client):
    r = make_client(CATALOG).post("/api/search")
    assert r.status_code == 400
def test_extension_415(make_client):
    assert upload(make_client(CATALOG), b"x", "a.txt").status_code == 415
def test_faux_jpg_400(make_client):
    assert upload(make_client(CATALOG), b"pas une image", "fake.jpg").status_code == 400
def test_trop_gros_413(make_client):
    assert upload(make_client(CATALOG), b"0" * (6 * 1024 * 1024), "big.jpg").status_code == 413
def test_resultats_ordonnes_sans_features(make_client):
    r = upload(make_client(CATALOG), png_bytes(), "q.png")
    res = r.get_json()["results"]
    assert [p["name"] for p in res] == ["cam1", "cam2"]
    assert res[0]["score"] >= res[1]["score"]
    assert "features" not in res[0]

    
def test_catalogue_vide(make_client):
    r = upload(make_client([]), png_bytes(), "q.png")
    assert r.status_code == 200 and r.get_json()["results"] == []


def test_produit_inconnu_404(make_client):
    assert make_client(CATALOG).get("/api/products/000000000000000000000000").status_code == 404


def test_id_invalide_404(make_client):
    assert make_client(CATALOG).get("/api/products/abc").status_code == 404