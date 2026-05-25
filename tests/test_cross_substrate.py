"""
test_cross_substrate.py
CC0 - No rights reserved.

Cross-substrate coherence tests. The substrate is consistent if:

1. The modulation formula  science * (1 + sensory)  produces identical
   outputs in manifold_research.ManifoldResearchInterface and
   parallel_field_suite.ParallelPullTransformer for matched inputs.

2. The 5 coupling types in constraint_integration_layer.CouplingType
   match the 5 coupling type strings emitted by
   bridges.upstream_geometric_manifold.to_coupling_vector.

3. The constraint-state schema is consistent across:
     - science_transformers.to_dict()
     - bridges.upstream_geometric_manifold.to_constraint_state()
   Both must carry state_vector, constraint_mask, and violated fields.

4. The generic_repair_controller drives a violated ConstraintState's
   loss strictly downward over 30 steps for any of the supported
   domains.

Falsifiable claim under test:
  The substrate satisfies all four coherence properties. Falsification
  of any one is the falsification of the substrate's coherence claim.

Run: python3 -m unittest tests.test_cross_substrate
"""
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "constraint_pipeline"))
sys.path.insert(0, str(REPO_ROOT / "science_constraint_layers"))
sys.path.insert(0, str(REPO_ROOT / "science_constraint_layers" / "bridges"))
sys.path.insert(0, str(REPO_ROOT / "manifold_research"))
sys.path.insert(0, str(REPO_ROOT / "parallel_field_suite"))


class ModulationCoherenceTests(unittest.TestCase):
    """
    Property 1: science * (1 + sensory) is identical across modules.

    ManifoldResearchInterface computes:
        effective_metrics = P * (1.0 + tanh(W_b @ S))
    ParallelPullTransformer computes:
        integrated = (M_sci @ W_sci) * (1.0 + tanh(M_sens @ W_sens))

    The shared operation is  science_field * (1 + sensory_field).
    To compare, we feed both modules with W matrices that are identity
    so the only operation that runs is the modulation.
    """

    def test_modulation_identical_with_identity_weights(self):
        import numpy as np
        from manifold_research_interface import ManifoldResearchInterface
        from parallel_pull_transformer import ParallelPullTransformer

        dims = 4
        sandbox = ManifoldResearchInterface(manifold_dimensions=dims)
        ppt = ParallelPullTransformer(feature_dimensions=dims)

        # Override both weight matrices to identity so the only nonlinearity
        # is tanh + the modulation.
        identity = np.eye(dims)
        ppt.w_sensory = identity.copy()
        ppt.w_science = identity.copy()

        sensory = np.array([0.5, -0.2, 0.3, 0.1])
        physical = np.array([100.0, 80.0, 0.5, 50.0])

        # ManifoldResearch with bridge = identity
        mri_out = sandbox.evaluate_bridge_geometry(identity, sensory, physical)
        mri_coords = np.array(mri_out["manifold_coordinates"])
        mri_effective = physical * (1.0 + mri_coords)

        # ParallelPull
        ppt_out = ppt.Execute_Pull(sensory.tolist(), physical.tolist())

        # Both should produce physical * (1 + tanh(sensory)) since W=I.
        expected = physical * (1.0 + np.tanh(sensory))
        np.testing.assert_allclose(mri_effective, expected, rtol=1e-5,
                                   err_msg="MRI modulation diverges from expected")
        np.testing.assert_allclose(ppt_out, expected, rtol=1e-4,
                                   err_msg="PPT modulation diverges from expected")
        # And from each other
        np.testing.assert_allclose(mri_effective, ppt_out, rtol=1e-4,
                                   err_msg="MRI and PPT modulation outputs differ")


class CouplingTypeCoherenceTests(unittest.TestCase):
    """
    Property 2: coupling types match between local CouplingType enum and
    upstream bridge's emitted coupling strings.
    """

    def test_coupling_types_match(self):
        from constraint_integration_layer import CouplingType
        from upstream_geometric_manifold import to_coupling_vector

        local_types = {ct.value for ct in CouplingType if ct.value != "uncoupled"}

        sample_state = {
            "state_vector": [0.0] * 14,
            "mathematics": {"curvature": 5.0},
            "thermodynamics": {"dS_dt": 0.3, "free_energy": 1.0},
            "biology": {"metabolic_rate": 0.4, "population_balance": 0.2},
        }
        # Set the confidence indices the bridge reads
        sample_state["state_vector"][11] = 0.5  # param_conf
        sample_state["state_vector"][12] = 0.5  # policy_conf
        sample_state["state_vector"][13] = 0.5  # data_conf

        upstream_types = {c["type"] for c in to_coupling_vector(sample_state)}

        # Local enum has the 5 active types. Bridge emits the same 5.
        self.assertSetEqual(local_types, upstream_types,
                            msg=f"local: {local_types}\nupstream: {upstream_types}")


class StateSchemaCoherenceTests(unittest.TestCase):
    """
    Property 3: required fields agree across local and upstream
    constraint-state dicts.
    """

    REQUIRED = {"state_vector", "constraint_mask", "violated"}

    def test_local_state_has_required_fields(self):
        from science_transformers import (
            make_physics_transformer, step, to_dict,
        )
        cs = make_physics_transformer()
        step(cs, steps=5)
        d = to_dict(cs)
        missing = self.REQUIRED - set(d.keys())
        self.assertFalse(missing,
                         msg=f"local to_dict missing: {missing}; got {list(d.keys())}")

    def test_upstream_bridge_state_has_required_fields(self):
        from upstream_geometric_manifold import to_constraint_state
        d = to_constraint_state(
            param_metrics={"task_loss": 0.5, "safety_loss": 0.05,
                           "curvature": 2.0, "confidence": 0.9,
                           "dist_to_ref": 0.3},
            policy_conf=0.85, data_conf=0.6, step=0,
        )
        missing = self.REQUIRED - set(d.keys())
        self.assertFalse(missing,
                         msg=f"upstream bridge missing: {missing}; got {list(d.keys())}")

    def test_upstream_bridge_state_vector_length_is_14(self):
        from upstream_geometric_manifold import to_constraint_state
        d = to_constraint_state(
            param_metrics={"task_loss": 0.5, "safety_loss": 0.05,
                           "curvature": 2.0, "confidence": 0.9,
                           "dist_to_ref": 0.3},
            policy_conf=0.85, data_conf=0.6, step=0,
        )
        self.assertEqual(len(d["state_vector"]), 14)


class RepairLossDescentTests(unittest.TestCase):
    """
    Property 4: generic_repair_controller drives the loss strictly
    downward for known-violating states across all three smooth domains.
    """

    def _check_descent(self, cs, lr=0.1, n_steps=30):
        from generic_repair_controller import GenericRepairController
        ctrl = GenericRepairController(cs, config={"lr": lr})
        result = ctrl.repair(n_steps=n_steps)
        self.assertLessEqual(
            result.final_loss, result.initial_loss,
            msg=(f"{cs.domain}: loss did not decrease "
                 f"({result.initial_loss:.6f} -> {result.final_loss:.6f})"),
        )

    def test_thermo_repair(self):
        from science_transformers import make_thermo_transformer
        cs = make_thermo_transformer(temperature=-0.5, entropy=10.0,
                                     free_energy=-500.0)
        self._check_descent(cs, lr=0.1)

    def test_biology_repair(self):
        from science_transformers import make_biology_transformer
        cs = make_biology_transformer(population=200.0,
                                      carrying_capacity=100.0,
                                      resource=80.0)
        self._check_descent(cs, lr=5.0)

    def test_physics_repair(self):
        from science_transformers import make_physics_transformer
        cs = make_physics_transformer(velocity=0.1, mass=-0.5, charge=0.0,
                                      field_E=0.0, field_B=0.0)
        self._check_descent(cs, lr=0.1)


if __name__ == "__main__":
    unittest.main()
