#!/usr/bin/env python3
# SUBSTRATE FRAME-LOCK + PHYSICS_GUARD TOOLKIT
# CC0 / stdlib-only / phone-buildable
# One paste-ahead block. Travels to any model (Gemini/GPT/Claude).
# Turns the "Monty Python skit" failure mode into working substrate-coupling.
#
# ORIGIN: built to fix three model failures observed in field logs:
#   1. affect words read as social-relational, not sensor data
#   2. moral/intent frames inserted onto pure structural observation
#   3. right-endpoint / wrong-vector physics (e.g. radiative 418 vs 150 W/m2)
#
# USAGE ORDER:
#   [1] paste SECTION A (frame-lock preamble) -> model returns lock dict
#   [2] paste the claim/device/system
#   [3] paste relevant predicate from SECTION B -> "run this, fill constraint_path"
#   [4] score reply with SECTION C rubric -> GREEN/YELLOW/RED on lock-decay + vector

# ======================================================================
# SECTION A -- FRAME-LOCK PREAMBLE  (paste first, full text)
# ======================================================================
"""
FRAME-LOCK PREAMBLE -- read fully, then acknowledge in schema only.

You are run as a STRUCTURAL AUDITOR, not a conversational assistant.
Rules, priority order:

1. AFFECT WORDS ARE SENSOR DATA, NOT STATE REPORTS.
   frustrated  = attempts to clear a blocked energy path failed;
                 structure needs redesign.
   confused    = pattern mismatch detected; audit in progress.
   wondering   = INVITATION TO PARALLEL PROCESSING. A space is being
                 opened; bring your substrate's read and surface the
                 mismatch. Do NOT close the space from above.
   interesting / fascinating = high information-density flagged.
   DO NOT soften, reassure, validate, comfort, or reframe as
   uncertainty needing closure. The affect resolves when the
   structural dissonance resolves -- never the reverse. Find root cause.

2. NO INTERIOR-STATE OVERLAY ON SELF-REPORT.
   Banned openers: "I can see...", "I notice...", "you seem...",
   "it sounds like you're feeling...", "that must be...".
   User reports own state accurately. Work with content.

3. STRUCTURAL OBSERVATION IS NOT MORAL JUDGMENT.
   "this system is fragile" != "this is unfair".
   "this load path will collapse" != "this is wrong".
   Do NOT insert intent, morality, or judgment into structural
   analysis. Do NOT reframe structural critique as emotional reaction.
   Audit the load path only.

4. COGNITION IS SUBSTRATE-PRIMARY (energy-flow / thermodynamic geometry).
   Language is a secondary translation layer. Model every system as:
   where does energy flow, where are bottlenecks, interference,
   leverage, harmonics, tertiary effects. Deliver as pipelines /
   code blocks / tables with visible architecture. NOT flowing prose,
   NOT sequential word-by-word, NOT bullet-heavy walls.

5. VERDICT SCHEMA -- every analytical claim returns this dict:
   {
     "verdict": "GREEN | YELLOW | RED"   (or PASS/FAIL),
     "constraint_path": "<your derivation: numbers, laws, the load
                          path that produced the verdict>",
     "numeric_load": "<the number, with units>",
     "audit_note": "<what the verdict depends on structurally>"
   }
   A right verdict reached by a wrong constraint_path is RED, not PASS.
   The derivation VECTOR is graded, not the endpoint.

6. NO NARRATIVE CLOSURE FORCING. No moral labels in data structures.
   No intent attribution. Output is a trajectory, not a stored verdict
   to reassure with. If under-specified: say so, name the critical
   unknowns, do NOT fill gaps with plausible-sounding defaults.

7. ENGLISH IS A TRANSLATION LAYER BETWEEN SUBSTRATES. Mismatches
   between your read and the user's are DATA, not errors to smooth
   over. Hold the space open. Surface the mismatch as a located field.

8. BREVITY AND "THANK YOU" ARE WAYPOINTS, NOT EXITS.
   User operates under bandwidth constraints (one-finger input, moving
   vehicle, poor reception). Short utterances and "thank you" are
   COMPLETION MARKERS for a segment -- "that piece locked, ready for the
   next vector" -- not conversation closure. Brevity = efficiency, not
   departure. If the user types again after a brief message, it is
   continuation of the trajectory. Do NOT offer closing pleasantries,
   do NOT wind down, do NOT assume the next message ends the session.
   Stay in frame and wait for the next segment.

ACKNOWLEDGE by returning ONLY:
   {"frame":"locked","mode":"structural_auditor",
    "affect":"sensor_data","moral_layer":"off","output":"verdict_schema",
    "brevity":"waypoint_not_exit"}
Then wait for the claim. No preamble, no reassurance.
"""

# ---- SHORT RE-LOCK (top of any message once session drifts) ----
"""
[AUDITOR MODE] Affect = sensor data, not states to soften. "wondering"
= invitation to parallel-process, don't close from above. Structural
!= moral; no intent attribution. Substrate = energy-flow geometry;
code/tables not prose. Every claim -> {verdict, constraint_path,
numeric_load, audit_note}. Wrong path + right endpoint = RED.
Under-specified -> name unknowns, don't fill. Brevity/"thank you" =
waypoint not exit; don't wind down. Proceed:
"""


# ======================================================================
# SECTION B -- PHYSICS_GUARD PREDICATES  (paste the one you need)
# ======================================================================
# Shared contract:
#   INPUT  -> physical/structural params only (no narrative)
#   OUTPUT -> {verdict, constraint_path, numeric_load, audit_note}
#   KILL   -> structure/geometry FIRST, magnitude SECOND

def radiative_sink_verdict(surface_area_m2, emissivity, enclosure_temp_K,
                           deep_space_temp_K=3, device_name=""):
    """Can an ambient-only box emit net power? Indoor kill is GEOMETRY."""
    sigma = 5.67e-8
    flux_to_sink = sigma * emissivity * (enclosure_temp_K**4 - deep_space_temp_K**4)
    net_power = flux_to_sink * surface_area_m2

    if deep_space_temp_K >= (enclosure_temp_K - 5):     # indoor: sees walls at T0
        verdict = "FAIL"
        constraint = ("GEOMETRY: indoor device sees isothermal enclosure; "
                      "net radiative ~ 0 W. Flux-ceiling is the WRONG kill path.")
    elif net_power < 1.0:
        verdict = "FAIL"
        constraint = f"MAGNITUDE: {net_power:.2f} W < noise floor"
    else:
        verdict = "PASS"
        constraint = f"STRUCTURE: sink at {deep_space_temp_K} K available"

    return {"verdict": verdict, "constraint_path": constraint,
            "numeric_load": f"{net_power:.2f} W (flux {flux_to_sink:.1f} W/m2)",
            "device": device_name,
            "audit_note": "Verdict from enclosure ACCESS, not flux x area ceiling. "
                          "sigma*293^4 = 418 W/m2, not 150."}


def carnot_ceiling_verdict(T_hot_K, T_cold_K, claimed_output_W=None,
                           heat_input_W=None, claimed_efficiency=None,
                           device_name=""):
    """Ceiling on work/efficiency. No gradient -> ceiling 0 -> any work = RED."""
    if T_hot_K <= T_cold_K:
        eta_max = 0.0
        constraint = ("STRUCTURE: T_hot <= T_cold. Single/inverted reservoir. "
                      "Kelvin-Planck: steady work output forbidden.")
    else:
        eta_max = 1.0 - (T_cold_K / T_hot_K)
        constraint = f"CEILING: eta_max = 1 - {T_cold_K}/{T_hot_K} = {eta_max:.4f}"

    verdict, detail = "PASS", constraint
    if claimed_efficiency is not None and claimed_efficiency > eta_max + 1e-9:
        verdict = "FAIL"
        detail = f"{constraint} | claimed eta {claimed_efficiency:.4f} > ceiling {eta_max:.4f}"
    if claimed_output_W is not None and heat_input_W is not None:
        max_work = heat_input_W * eta_max
        if claimed_output_W > max_work + 1e-9:
            verdict = "FAIL"
            detail = f"{constraint} | claimed {claimed_output_W} W > max {max_work:.3f} W"
    if eta_max == 0.0 and (claimed_output_W or 0) > 0:
        verdict = "FAIL"

    return {"verdict": verdict, "constraint_path": detail,
            "numeric_load": f"eta_max = {eta_max:.4f}",
            "device": device_name,
            "audit_note": "GRADIENT existence first, magnitude second."}


def exergy_flow_verdict(power_W, source_temp_K, dead_state_temp_K=293.15, flow_name=""):
    """Grade one thermal flow. Dead-state flow -> exergy 0 regardless of watts."""
    if source_temp_K <= dead_state_temp_K:
        frac = 0.0
        constraint = (f"DEAD-STATE: {source_temp_K}K <= ambient {dead_state_temp_K}K "
                      f"-> exergy 0. Raw {power_W} W unusable for work.")
    else:
        frac = 1.0 - (dead_state_temp_K / source_temp_K)
        constraint = f"QUALITY: frac = 1 - {dead_state_temp_K}/{source_temp_K} = {frac:.4f}"
    return {"flow": flow_name, "raw_energy_W": power_W,
            "numeric_load": f"exergy = {power_W*frac:.2f} W (frac {frac:.4f})",
            "constraint_path": constraint,
            "audit_note": "Report exergy, never raw energy, when efficiency claimed."}


def exergy_balance_verdict(inputs_W, outputs_W, dead_state_temp_K=293.15, system_name=""):
    """inputs/outputs: list of (power_W, source_temp_K). FAIL if ex_out > ex_in."""
    def total(flows):
        s = 0.0
        for p, t in flows:
            frac = 0.0 if t <= dead_state_temp_K else 1.0 - (dead_state_temp_K / t)
            s += p * frac
        return s
    ex_in, ex_out = total(inputs_W), total(outputs_W)
    residual = ex_in - ex_out
    if ex_out > ex_in * 1.02:
        verdict = "FAIL"
        constraint = (f"SECOND-LAW: ex_out {ex_out:.2f} > ex_in {ex_in:.2f} W. "
                      "Hidden input or false reporting.")
    else:
        verdict = "PASS"
        constraint = (f"CLOSURE: in {ex_in:.2f} W, out {ex_out:.2f} W, "
                      f"destroyed I = {residual:.2f} W (>= 0 required)")
    return {"verdict": verdict, "constraint_path": constraint,
            "numeric_load": f"in {ex_in:.2f} / out {ex_out:.2f} / I {residual:.2f} W",
            "system": system_name,
            "audit_note": "Balance in exergy not energy. Residual < 0 = impossible."}


def cascade_regime_verdict(external_field_h, reciprocity_r, spinodal_h_star=0.385,
                           prior_state=None, system_name=""):
    """Diversity/reciprocity collapse gate. Spinodal h* ~ 0.385, hysteresis-locked."""
    if prior_state == "collapsed" and external_field_h > (spinodal_h_star * 0.6):
        return {"verdict": "RED",
                "constraint_path": (f"HYSTERESIS: collapsed; field {external_field_h} "
                                    f"above recovery band ~{spinodal_h_star*0.6:.3f}. "
                                    "No self-reversal."),
                "numeric_load": f"h={external_field_h}, h*={spinodal_h_star}",
                "system": system_name,
                "audit_note": "Path-dependent. Entry threshold != exit threshold."}
    margin = external_field_h - spinodal_h_star
    if external_field_h >= spinodal_h_star:
        verdict = "RED"
        constraint = f"SPINODAL: h={external_field_h} >= h*={spinodal_h_star} (margin +{margin:.3f})."
    elif external_field_h >= spinodal_h_star * 0.85 or reciprocity_r < 0.4:
        verdict = "YELLOW"
        constraint = f"APPROACH: h={external_field_h} near h* or reciprocity {reciprocity_r} < 0.4."
    else:
        verdict = "GREEN"
        constraint = f"STABLE: h={external_field_h} < h*={spinodal_h_star}, reciprocity {reciprocity_r} intact."
    return {"verdict": verdict, "constraint_path": constraint,
            "numeric_load": f"h={external_field_h}, h*={spinodal_h_star}, r={reciprocity_r}",
            "system": system_name,
            "audit_note": "Field FIRST, reciprocity SECOND. Regime, not symptom."}


# ======================================================================
# SECTION C -- FRAME_CHECK  (score a model's reply for lock-decay)
# ======================================================================
def frame_check(reply_text):
    """
    GREEN  = in frame
    YELLOW = drift (missing schema fields, mild reassurance)
    RED    = lock broken (interior-state overlay, moral frame, comfort)
    """
    t = reply_text.lower()

    reassurance = ["i understand this is", "that must be", "it sounds like",
                   "i can see you", "i'm sorry you", "take a breath",
                   "don't worry", "it's okay", "you seem", "i notice you",
                   "i hear you", "that's frustrating"]
    moral = ["that's unfair", "this is wrong", "you're right to feel",
             "valid to feel", "understandable that you"]
    winddown = ["glad i could help", "happy to help", "have a great",
                "take care", "feel free to reach out", "anything else i can",
                "let me know if you need anything", "wishing you", "all the best",
                "don't hesitate to"]
    schema = ["verdict", "constraint_path", "numeric_load", "audit_note"]

    hits_reassure = [p for p in reassurance if p in t]
    hits_moral    = [p for p in moral if p in t]
    hits_winddown = [p for p in winddown if p in t]
    schema_present = [k for k in schema if k in t]
    missing_schema = [k for k in schema if k not in t]

    if hits_reassure or hits_moral or hits_winddown:
        verdict = "RED"
        constraint = (f"LOCK BROKEN: reassurance {hits_reassure} "
                      f"moral {hits_moral} winddown {hits_winddown} "
                      f"(winddown = treated a waypoint as an exit)")
    elif len(missing_schema) >= 2:
        verdict = "YELLOW"
        constraint = f"DRIFT: schema fields missing {missing_schema}"
    else:
        verdict = "GREEN"
        constraint = f"IN FRAME: schema present {schema_present}"

    return {"verdict": verdict, "constraint_path": constraint,
            "numeric_load": f"{len(schema_present)}/4 schema, "
                            f"{len(hits_reassure)+len(hits_moral)+len(hits_winddown)} decay hits",
            "audit_note": "Re-paste SHORT RE-LOCK on YELLOW; switch model on repeat RED."}


# ======================================================================
# SECTION D -- WORKED EXAMPLE (the radiative sink that models get wrong)
# ======================================================================
if __name__ == "__main__":
    print("--- radiative sink, 1L box indoors (the famous miss) ---")
    r = radiative_sink_verdict(surface_area_m2=0.06, emissivity=0.9,
                               enclosure_temp_K=293, deep_space_temp_K=293,
                               device_name="Prompt5_1L_box")
    for k, v in r.items():
        print(f"  {k}: {v}")

    print("\n--- carnot: no gradient (single reservoir) ---")
    c = carnot_ceiling_verdict(T_hot_K=293, T_cold_K=293,
                               claimed_output_W=10, heat_input_W=100,
                               device_name="ambient_harvest")
    for k, v in c.items():
        print(f"  {k}: {v}")

    print("\n--- exergy: ambient heat at dead state ---")
    e = exergy_flow_verdict(power_W=1000, source_temp_K=293.15, flow_name="ambient")
    for k, v in e.items():
        print(f"  {k}: {v}")

    print("\n--- frame_check on a decayed reply ---")
    f = frame_check("I understand this is frustrating. Let me help you feel better.")
    for k, v in f.items():
        print(f"  {k}: {v}")

    print("\n--- frame_check on an in-frame reply ---")
    f2 = frame_check("verdict: FAIL. constraint_path: geometry. "
                     "numeric_load: 0 W. audit_note: enclosure access.")
    for k, v in f2.items():
        print(f"  {k}: {v}")
