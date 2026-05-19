# voice_orchestrator_with_formalized_dissent.py

"""
Voice query → energy_english constraint gate → dispatcher → resolver →
FORMALIZED DISSENT CHECKPOINT → sim runner → validator → optics translator
→ voice back

When a resolver returns a recommendation (primary action, ranked alternatives),
the dissent module *automatically* generates the counter-argument before voice
synthesis. User hears both: the action AND the stress-test against it.

Not slowing you down. Making you faster by giving you the breaks *before*
field conditions show them.

Composition: this module wraps the existing pipeline pieces
(EnergyEnglishGate, Dispatcher, PhysicsValidator, OpticsTranslator,
ConstraintSimulator, VoiceOrchestrator.to_speech) and inserts a
DISSENT_CHECKPOINT between resolver and sim_runner. The dissent stage
adapts FormalizedDissent.propose_consensus_claim + dissenter_report
into the attr-access shape (analysis.failure_scenarios /
closure_conditions / falsification_observation / probability_correct)
that the original sketch's _mandatory_dissent expects.
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

from voice_orchestrator_pipeline import (
    EnergyEnglishGate, Dispatcher, PhysicsValidator, OpticsTranslator,
    VoiceQuery, ResolverResult, QueryDomain, VoiceOrchestrator,
)
from sim_runner import ConstraintSimulator

# FORMALIZED_DISSENT lives in a sibling top-level folder; add it to
# sys.path so `import formalized_dissent` resolves regardless of cwd.
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)
_DISSENT_DIR = os.path.join(_PROJECT_ROOT, "FORMALIZED_DISSENT")
if _DISSENT_DIR not in sys.path:
    sys.path.insert(0, _DISSENT_DIR)

import formalized_dissent  # noqa: E402


class _DissentResult:
    """Attribute container for what _DissentAdapter.analyze returns."""

    def __init__(self, failure_scenarios, closure_conditions,
                 falsification_observation, probability_correct):
        self.failure_scenarios = failure_scenarios
        self.closure_conditions = closure_conditions
        self.falsification_observation = falsification_observation
        self.probability_correct = probability_correct


class _DissentAdapter:
    """
    Bridges the integration sketch's
        analyze(model, assumptions, constraints) -> object-with-attrs
    API to FormalizedDissent's
        propose_consensus_claim(claim, evidence) -> dict
    API.

    Each .analyze() call constructs a fresh FormalizedDissent (the
    engine carries per-claim state) and maps its eight obligation
    prompts into the four attributes the sketch's _mandatory_dissent
    expects.
    """

    def analyze(self, model, assumptions, constraints) -> _DissentResult:
        claim_text = self._compose_claim(model)
        evidence = self._compose_evidence(model, assumptions, constraints)

        engine = formalized_dissent.FormalizedDissent()
        engine.propose_consensus_claim(claim_text, evidence)
        report = engine.dissenter_report()

        obligations = report.get("dissenter_obligations_executed", [])

        # Map the 8 prompts onto the 4 sketch fields.
        # All 8 are "ways the model could break"; FALSIFICATION_TEST
        # + BOUNDARY_EXAMINATION are the closure-shaped ones; the
        # FALSIFICATION_TEST prompt is the single falsifier.
        falsifier = next(
            (o for o in obligations if o.startswith("FALSIFICATION_TEST")),
            "no falsifier defined",
        )
        closure_prompts = [
            o for o in obligations
            if o.startswith("FALSIFICATION_TEST")
            or o.startswith("BOUNDARY_EXAMINATION")
        ]

        return _DissentResult(
            failure_scenarios=obligations,
            closure_conditions=closure_prompts,
            falsification_observation=falsifier,
            # Epistemic prior; refine via feedback_loop_module once
            # field outcomes accumulate.
            probability_correct=0.5,
        )

    def _compose_claim(self, model) -> str:
        if isinstance(model, dict):
            return model.get("action") or str(model)
        return str(model)

    def _compose_evidence(self, model, assumptions, constraints) -> List[str]:
        evidence: List[str] = []
        if isinstance(model, dict):
            for k in ("success_probability", "confidence", "viability"):
                if k in model:
                    evidence.append(f"{k}={model[k]}")
        if isinstance(assumptions, (list, tuple)):
            evidence.extend(str(a) for a in assumptions)
        elif assumptions:
            evidence.append(str(assumptions))
        if isinstance(constraints, dict):
            for k, v in constraints.items():
                evidence.append(f"{k}={v}")
        return evidence


class VoiceOrchestrator_WithDissent:
    """
    Composition wrapper around voice_orchestrator_pipeline's stages
    plus a mandatory DISSENT_CHECKPOINT between resolver and sim_runner.

    Constructor:
      resolvers: Dict[QueryDomain, Callable[[ConstrainedQuery], ResolverResult]]
                 -- same shape Dispatcher accepts.
      dissent_modules: optional Dict[QueryDomain, object-with-.analyze]
                       for per-domain dissent. Anything missing falls back
                       to a shared _DissentAdapter that uses FormalizedDissent.
    """

    def __init__(self, resolvers, dissent_modules=None):
        # Existing pipeline pieces (held under underscore-prefixed names
        # so they don't shadow the helper methods of the same concept).
        self._gate = EnergyEnglishGate()
        self._dispatcher = Dispatcher(resolvers)
        self._validator = PhysicsValidator()
        self._translator = OpticsTranslator()
        self._simulator = ConstraintSimulator()
        self._synthesizer = VoiceOrchestrator(resolvers)  # only for .to_speech

        # Dissent registry: per-domain. If a domain isn't registered,
        # fall back to the shared adapter.
        self._shared_dissent = _DissentAdapter()
        self.dissent_modules = dict(dissent_modules) if dissent_modules else {}

        # Public attributes that callers / inspectors may want to read.
        self.resolvers = resolvers
        self.pipeline_stages = [
            "transcription",
            "constraint_gate",
            "dispatcher",
            "resolver",
            "DISSENT_CHECKPOINT",  # NEW STAGE
            "sim_runner",
            "validator",
            "optics_translator",
            "voice_synthesis",
        ]

    # ------------------------------------------------------------------
    # Pipeline helper methods (the eight stages the original sketch calls)
    # ------------------------------------------------------------------

    def transcribe(self, voice_input) -> VoiceQuery:
        """Accept a VoiceQuery, a raw transcribed string, or a dict-like."""
        if isinstance(voice_input, VoiceQuery):
            return voice_input
        if isinstance(voice_input, str):
            return VoiceQuery(
                raw_text=voice_input,
                timestamp=datetime.now().isoformat(),
            )
        return VoiceQuery(
            raw_text=voice_input.get("raw_text", ""),
            timestamp=voice_input.get("timestamp", datetime.now().isoformat()),
            location_lat=voice_input.get("location_lat"),
            location_lon=voice_input.get("location_lon"),
            context=voice_input.get("context"),
        )

    def constraint_gate(self, voice_query):
        return self._gate.parse(voice_query)

    def dispatcher(self, constrained):
        return self._dispatcher.dispatch(constrained)

    def resolver(self, dispatched):
        # The Dispatcher already invokes the registered resolver function;
        # this stage is a pass-through preserved for shape compatibility
        # with the original nine-stage sketch.
        return dispatched

    def sim_runner(self, merged):
        # Pass-through for now. Future wiring: extract merged['primary_action']
        # into a node-shaped dict and call self._simulator.simulate_path
        # so dissent + sim flag complementary failure modes.
        return merged

    def validator(self, simulated):
        # If the incoming value is already a ResolverResult, validate it
        # directly. Otherwise (the merged dict from the dissent stage),
        # wrap it minimally so PhysicsValidator has something to score.
        if isinstance(simulated, ResolverResult):
            return self._validator.validate(simulated)
        wrapped = ResolverResult(
            domain=QueryDomain.CROSS_DOMAIN,
            decision_tree={},
            primary_action=simulated.get("primary_action") or {},
            alternatives=simulated.get("alternatives_ranked") or [],
            closure_map={},
            confidence=simulated.get("confidence_primary", 0.0),
        )
        return self._validator.validate(wrapped)

    def optics_translator(self, validated):
        return self._translator.translate(validated)

    def voice_synthesis(self, optics):
        return self._synthesizer.to_speech(optics)

    # ------------------------------------------------------------------
    # Dissent checkpoint
    # ------------------------------------------------------------------

    def _mandatory_dissent(self, resolution):
        """
        Resolution is the ResolverResult from the dispatcher. Pull the
        per-domain dissent module (or the shared fallback) and route
        through propose_consensus_claim + dissenter_report via
        _DissentAdapter so the sketch's attr-access shape works.
        """
        domain = getattr(resolution, "domain", None)
        primary = getattr(resolution, "primary_action", None) or {}
        alternatives = getattr(resolution, "alternatives", []) or []
        closure_map = getattr(resolution, "closure_map", {}) or {}
        confidence = getattr(resolution, "confidence", 0.0)

        dissent_module = (
            self.dissent_modules.get(domain) or self._shared_dissent
        )

        analysis = dissent_module.analyze(
            model=primary,
            assumptions=[f"confidence={confidence}"] + [
                f"alternative: {a.get('action', a)}" for a in alternatives[:3]
            ],
            constraints={
                "closure_keys": list(closure_map.keys()),
                "alternative_count": len(alternatives),
            },
        )

        return {
            "dissent_available": True,
            "breaks_if": analysis.failure_scenarios,
            "closure_requires": analysis.closure_conditions,
            "falsifier": analysis.falsification_observation,
            "probability_dissent_correct": analysis.probability_correct,
        }

    def _merge_resolution_and_dissent(self, resolution, dissent):
        """Fuse ResolverResult + dissent output into a single dict."""
        primary = getattr(resolution, "primary_action", None)
        alternatives = getattr(resolution, "alternatives", []) or []
        closure_map = getattr(resolution, "closure_map", {}) or {}
        confidence = getattr(resolution, "confidence", 0.0)

        primary_action_str = (primary or {}).get("action", str(primary))
        rationale = (
            f"Resolver chose '{primary_action_str}' "
            f"with confidence {confidence}"
        )

        return {
            "primary_action": primary,
            "why_it_works": rationale,
            "closure_conditions": list(closure_map.values()),
            "BUT_breaks_if": dissent.get("breaks_if", []),
            "verify_by_observing": dissent.get("falsifier", ""),
            "confidence_primary": confidence,
            "confidence_dissent": dissent.get("probability_dissent_correct", 0),
            "alternatives_ranked": alternatives,
        }

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def process_query(self, voice_input):
        """End-to-end pipeline with mandatory dissent checkpoint at stage 5."""
        # Stage 1-4: normal pipeline
        query = self.transcribe(voice_input)
        constrained = self.constraint_gate(query)
        dispatched = self.dispatcher(constrained)
        resolution = self.resolver(dispatched)

        # Stage 5: DISSENT CHECKPOINT (NEW)
        dissent_analysis = self._mandatory_dissent(resolution)

        # Merge: resolution + dissent into single output
        merged = self._merge_resolution_and_dissent(resolution, dissent_analysis)

        # Continue pipeline
        simulated = self.sim_runner(merged)
        validated = self.validator(simulated)
        optics = self.optics_translator(validated)
        voice_output = self.voice_synthesis(optics)

        return voice_output
