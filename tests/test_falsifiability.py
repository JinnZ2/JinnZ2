"""
test_falsifiability.py
CC0 - No rights reserved.

Tests that every CLAIM_TABLE-emitting module in the substrate produces
well-formed claim tables. Each claim must carry:
  - claim_id            (string, non-empty)
  - claim               (string, non-empty)
  - falsification_condition  (string)
  - status              (string)

The "falsification_condition" field is the load-bearing one. A claim
without one is rhetoric, not a falsifiable claim. This test set is the
mechanical enforcement of the corpus-hardening rule.

Falsifiable claim under test:
  Every CLAIM_TABLE-emitting module in this substrate produces claims
  with the four required fields. Falsification: find a module whose
  emitted claim is missing one of those fields.

Run: python3 -m unittest tests.test_falsifiability
"""
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "constraint_pipeline"))
sys.path.insert(0, str(REPO_ROOT / "science_constraint_layers"))
sys.path.insert(0, str(REPO_ROOT / "science_constraint_layers" / "bridges"))


REQUIRED_FIELDS = {"claim_id", "claim", "falsification_condition", "status"}


def assert_claims_well_formed(test_case, claims, source_label):
    """Helper. Asserts every claim in `claims` carries REQUIRED_FIELDS."""
    test_case.assertGreater(len(claims), 0,
                            msg=f"{source_label}: no claims emitted")
    for i, c in enumerate(claims):
        missing = REQUIRED_FIELDS - set(c.keys())
        test_case.assertFalse(
            missing,
            msg=f"{source_label} claim #{i} missing fields: {missing}; "
                f"got keys: {list(c.keys())}",
        )
        for field in ("claim_id", "claim", "status"):
            test_case.assertTrue(
                isinstance(c[field], str) and c[field].strip(),
                msg=f"{source_label} claim #{i} field {field!r} is empty or non-string",
            )
        # falsification_condition is allowed to be the literal N/A string
        # only for KNOWN_LIMITATION status.
        if c["status"] == "KNOWN_LIMITATION":
            test_case.assertIsNotNone(c["falsification_condition"])
        else:
            test_case.assertTrue(
                isinstance(c["falsification_condition"], str) and
                c["falsification_condition"].strip(),
                msg=f"{source_label} claim #{i} has no falsification condition",
            )


class CorpusFalsifiabilityTests(unittest.TestCase):

    def test_grammatical_constraint_encoder(self):
        import grammatical_constraint_encoder as m
        table = m.encode_to_claim_table(
            "We are going forward whilst the path holds.", "test"
        )
        self.assertIn("claims", table)
        assert_claims_well_formed(self, table["claims"], "grammatical_encoder")

    def test_token_constraint_validator(self):
        import token_constraint_validator as m
        results = [m.validate("Obviously this proves that everyone knows.")]
        table = m.to_claim_table(results, "test")
        assert_claims_well_formed(self, table["claims"], "token_validator")

    def test_constraint_tokenizer(self):
        import constraint_tokenizer as m
        cbus = m.tokenize("We are going forward whilst the path holds.")
        table = m.to_claim_table(cbus, "test")
        assert_claims_well_formed(self, table["claims"], "constraint_tokenizer")

    def test_numeric_token_mapper(self):
        import numeric_token_mapper as m
        ids, vocab = m.tokenize("We are going forward whilst the path holds.")
        table = m.to_claim_table(ids, vocab, "test")
        assert_claims_well_formed(self, table["claims"], "numeric_token_mapper")

    def test_bpe_constraint_tokenizer(self):
        import bpe_constraint_tokenizer as m
        corpus = [
            "We are going forward whilst the path holds.",
            "Going forward and oft the constraint shifts.",
            "Oft the path is forward-going.",
        ]
        vocab = m.build_bpe(corpus, num_merges=10)
        table = m.to_claim_table(vocab, "test")
        assert_claims_well_formed(self, table["claims"], "bpe_tokenizer")

    def test_voice_tokenizer(self):
        import voice_tokenizer as m
        tokens = m.tokenize("um — we are going forward, actually no")
        table = m.to_claim_table(tokens, "test")
        assert_claims_well_formed(self, table["claims"], "voice_tokenizer")

    def test_constraint_integration_layer(self):
        from science_transformers import (
            make_physics_transformer, make_biology_transformer,
            make_thermo_transformer, make_math_transformer,
            step, to_dict,
        )
        import constraint_integration_layer as m
        transformers = [
            make_physics_transformer(), make_biology_transformer(),
            make_thermo_transformer(), make_math_transformer(),
        ]
        for cs in transformers:
            step(cs, steps=20)
        ics = m.integrate([to_dict(cs) for cs in transformers])
        table = m.to_claim_table(ics, "test")
        assert_claims_well_formed(self, table["claims"], "constraint_integration")

    def test_geometric_controller(self):
        from geometric_metric_stdlib import GeometricControllerStdlib
        cfg = {"lr": 0.05, "mu_repair": 0.1, "fd_epsilon": 1e-4,
               "n_fisher_samples": 4, "spectral_C_bound": 5.0}
        ctrl = GeometricControllerStdlib([0.0, 0.0],
                                          lambda t: sum(x * x for x in t),
                                          cfg)
        theta = [1.0, -0.5]
        for _ in range(5):
            theta, _ = ctrl.step(theta)
        table = ctrl.to_claim_table("test", path="/tmp/_test_geom_claims.json")
        assert_claims_well_formed(self, table["claims"], "geometric_controller")

    def test_required_fields_set_is_stable(self):
        """
        Meta-test: REQUIRED_FIELDS must include 'falsification_condition'.
        If a future refactor drops it, this test catches the regression.
        """
        self.assertIn("falsification_condition", REQUIRED_FIELDS)
        self.assertIn("claim_id", REQUIRED_FIELDS)
        self.assertIn("claim", REQUIRED_FIELDS)
        self.assertIn("status", REQUIRED_FIELDS)


if __name__ == "__main__":
    unittest.main()
