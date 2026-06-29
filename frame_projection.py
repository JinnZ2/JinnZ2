# frame_projection.py
# CC0. stdlib only.
# A projection is a frame-relative scalar built from a raw axis vector.
# The scalar is NOT an invariant (SITUATEDNESS.md §2.5).
# Every call is stamped: frame name, weights used, is_invariant=False.
# There is no default frame. Scalars are opt-in and always labeled.

def project(axis_vector, weights, frame_name="unnamed"):
    """
    Produce a scalar from axis_vector under the declared weighting.
    weights: dict axis -> weight (need not sum to 1; renormalized here).
    Axes in weights but absent from axis_vector contribute 0.
    Returns: {"value": float, "frame": str, "is_invariant": False,
              "weights_used": dict of renormalized weights}
    """
    total_w = sum(weights.values())
    if total_w <= 0:
        return {"value": 0.0, "frame": frame_name,
                "is_invariant": False, "weights_used": {}}
    norm = {k: round(v / total_w, 6) for k, v in weights.items()}
    value = sum(norm[k] * float(axis_vector.get(k, 0.0)) for k in norm)
    return {"value": round(value, 4), "frame": frame_name,
            "is_invariant": False, "weights_used": norm}


def compare_projections(axis_vector, frames):
    """
    frames: list of (name, weights_dict) tuples.
    Runs project() under each declared frame. The spread across them
    demonstrates that the vector contains no single preferred scalar —
    different weighting choices produce different rankings.
    Returns: {"projections": list of project() results, "spread": float}
    """
    results = [project(axis_vector, w, name) for name, w in frames]
    values = [r["value"] for r in results]
    spread = round(max(values) - min(values), 4) if len(values) > 1 else 0.0
    return {"projections": results, "spread": spread}
