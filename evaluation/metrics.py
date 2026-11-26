"""Metriques d'evaluation : fonctions PURES (testables sans Mongo ni TensorFlow)."""
from collections import defaultdict
 
 
def precision_at_k(categories, expected, k):
    """Part des k premiers resultats qui sont de la bonne categorie.
    On divise TOUJOURS par k : si le seuil renvoie moins de k resultats, la precision baisse."""
    return sum(c == expected for c in categories[:k]) / k
 
 
def evaluate(rows, retrieve, ks=(5, 10)):
    """rows     : [{'file': ..., 'expected_category': ...}, ...]
    retrieve : fonction file -> [(categorie, score), ...] triee du plus au moins similaire.
    Renvoie {'per_category': {...}, 'global': {...}, 'failures': [...]}."""
    acc = defaultdict(lambda: {"n": 0, "top1": 0, **{k: 0.0 for k in ks}})
    failures = []
    for row in rows:
        expected = row["expected_category"].strip().lower()
        hits = retrieve(row["file"])
        cats = [c for c, _ in hits]
        s = acc[expected]
        s["n"] += 1
        for k in ks:
            s[k] += precision_at_k(cats, expected, k)
        ok = bool(cats) and cats[0] == expected
        s["top1"] += int(ok)
        if not ok:
            failures.append({
                "file": row["file"], "expected": expected,
                "top1_category": cats[0] if cats else "",
                   "top1_score": round(hits[0][1], 3) if hits else "",
                "top5": " ".join(cats[:5]),
            })
 
    report = {"per_category": {}, "global": {}, "failures": failures}
    total = sum(s["n"] for s in acc.values())
    for cat, s in sorted(acc.items()):
        report["per_category"][cat] = {"n": s["n"], "top1": s["top1"] / s["n"],
                                       **{k: s[k] / s["n"] for k in ks}}
    if total:
        report["global"] = {"n": total,
                            "top1": sum(s["top1"] for s in acc.values()) / total,
                            **{k: sum(s[k] for s in acc.values()) / total for k in ks}}
    return report
 
 
def threshold_table(relevant_scores, irrelevant_scores, thresholds):
    """Pour chaque seuil : % de requetes pertinentes gardees
    et % de requetes hors catalogue rejetees."""
    rows = []
    for t in thresholds:
        n_rel, n_irr = len(relevant_scores), len(irrelevant_scores)
        kept = sum(s >= t for s in relevant_scores) / n_rel if n_rel else 0.0
        rejected = sum(s < t for s in irrelevant_scores) / n_irr if n_irr else 0.0
        rows.append({"threshold": round(t, 2), "relevant_kept": kept,
                     "irrelevant_rejected": rejected, "balanced": (kept + rejected) / 2})
    return rows
 
 
def best_threshold(rows):
    """Parmi les seuils qui maximisent la moyenne (gardees + rejetees), prend celui du MILIEU
    du plateau : plus robuste qu'un seuil colle a la limite d'un groupe."""
    top = max(r["balanced"] for r in rows)
    plateau = [r["threshold"] for r in rows if r["balanced"] == top]
    return plateau[len(plateau) // 2]
