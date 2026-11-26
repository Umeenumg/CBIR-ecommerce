import sys
from pathlib import Path
 
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "evaluation"))
 
from metrics import best_threshold, evaluate, precision_at_k, threshold_table
 
 
def test_precision_at_k_exemple():
    cats = ["camera", "camera", "laptop", "camera", "handbag"]
    assert precision_at_k(cats, "camera", 5) == 0.6
    assert precision_at_k(cats, "camera", 2) == 1.0
 
 
def test_precision_divise_par_k_meme_si_peu_de_resultats():
    assert precision_at_k(["camera"], "camera", 5) == 0.2      # 1 bon resultat sur k=5
    assert precision_at_k([], "camera", 5) == 0.0
 
 
def test_evaluate_global_par_categorie_et_echecs():
    answers = {
        "cam_q1.jpg": [("camera", .9), ("camera", .8), ("laptop", .7),
                       ("camera", .6), ("camera", .5)],
        "lap_q1.jpg": [("camera", .9), ("laptop", .8), ("laptop", .7),
                       ("laptop", .6), ("laptop", .5)],
    }
    rows = [{"file": "cam_q1.jpg", "expected_category": "camera"},
            {"file": "lap_q1.jpg", "expected_category": "laptop"}]
    rep = evaluate(rows, lambda f: answers[f], ks=(5,))
    assert rep["per_category"]["camera"][5] == 0.8
    assert rep["per_category"]["laptop"][5] == 0.8
    assert rep["global"]["top1"] == 0.5
    assert [x["file"] for x in rep["failures"]] == ["lap_q1.jpg"]
    assert rep["failures"][0]["top1_category"] == "camera"
 
 
def test_threshold_table_et_meilleur_seuil():
    relevant = [0.9, 0.85, 0.8, 0.75]
    irrelevant = [0.5, 0.55, 0.6, 0.7]
    rows = threshold_table(relevant, irrelevant, [0.5, 0.65, 0.72, 0.95])
    by_t = {r["threshold"]: r for r in rows}
    assert by_t[0.5]["relevant_kept"] == 1.0 and by_t[0.5]["irrelevant_rejected"] == 0.0
    assert by_t[0.72]["relevant_kept"] == 1.0 and by_t[0.72]["irrelevant_rejected"] == 1.0
    assert by_t[0.95]["relevant_kept"] == 0.0
    assert best_threshold(rows) == 0.72
 
 
def test_best_threshold_prend_le_milieu_du_plateau():
    rows = threshold_table([0.9, 0.9], [0.4, 0.4], [0.3, 0.5, 0.6, 0.7, 0.95])
    # 0.5, 0.6, 0.7 sont parfaits -> le milieu est 0.6
    assert best_threshold(rows) == 0.6
