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
"""

class VoiceOrchestrator_WithDissent:
    def __init__(self, resolvers, dissent_modules):
        self.resolvers = resolvers
        self.dissent_modules = dissent_modules  # one per domain
        self.pipeline_stages = [
            "transcription",
            "constraint_gate",
            "dispatcher",
            "resolver",
            "DISSENT_CHECKPOINT",  # NEW STAGE
            "sim_runner",
            "validator",
            "optics_translator",
            "voice_synthesis"
        ]

    def process_query(self, voice_input):
        """Query flows through pipeline. Dissent fires automatically."""

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

    def _mandatory_dissent(self, resolution):
        """
        Resolver says: "Primary action is X, alternatives are Y and Z."
        Dissent says: "X assumes [these things]. It breaks if [these fail]."
        """
        domain = resolution["domain"]
        dissent_module = self.dissent_modules.get(domain)

        if not dissent_module:
            return {"dissent_available": False}

        # Automatically generate counter-argument
        analysis = dissent_module.analyze(
            model=resolution["primary_action"],
            assumptions=resolution["stated_assumptions"],
            constraints=resolution["constraints"]
        )

        return {
            "dissent_available": True,
            "breaks_if": analysis.failure_scenarios,
            "closure_requires": analysis.closure_conditions,
            "falsifier": analysis.falsification_observation,
            "probability_dissent_correct": analysis.probability_correct
        }

    def _merge_resolution_and_dissent(self, resolution, dissent):
        """
        Output includes both the resolver's recommendation AND the
        stress-test against it. User gets the full picture in one query.
        """
        return {
            "primary_action": resolution["primary_action"],
            "why_it_works": resolution["rationale"],
            "closure_conditions": resolution["closure_conditions"],
            "BUT_breaks_if": dissent.get("breaks_if", []),
            "verify_by_observing": dissent.get("falsifier", ""),
            "confidence_primary": resolution["confidence"],
            "confidence_dissent": dissent.get("probability_dissent_correct", 0),
            "alternatives_ranked": resolution["alternatives"]
        }
