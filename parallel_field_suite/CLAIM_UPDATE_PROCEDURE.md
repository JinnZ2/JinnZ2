# CLAIM UPDATE PROCEDURE — parallel_field_suite

**Workflow** for incorporating new evidence (arXiv preprint, peer-reviewed
paper, direct observation, falsification report) into the claim table
without losing the prior version.

License: CC0.

---

## Steps

1. **Identify the trigger.**
   - new paper (arXiv ID, DOI, or peer-reviewed citation)
   - new direct observation (date, observer, conditions)
   - falsification report (GitHub issue with evidence)
   - cross-repo update (another JinnZ2 repo emitted a superseding claim)

2. **Locate the affected claim(s).**
   Read `CLAIM_TABLE.json`. Identify entries whose `claim` or
   `evidence_basis` or `probability_estimate` is affected by the
   trigger.

3. **Decide on update reason.**
   One of: `new_evidence`, `error_correction`, `scope_refinement`,
   `falsification_partial`. See `CLAIM_TABLE_VERSIONING.md`.

4. **Create a new versioned entry.**
   - id = `<old_id>_v<N+1>` (or follow the local convention)
   - `current: true`
   - `supersedes: <old_id>`
   - `update_reason: <one of the four>`
   - `update_source: <citation, DOI, commit hash, or issue link>`

5. **Mark the prior entry as superseded.**
   - `current: false`
   - `superseded_by: <new_id>`
   - Do NOT delete the prior entry.

6. **Add a test.**
   - new file: `tests/test_<new_id>.py`
   - The test validates the new claim against expected output.
   - If the prior test (`tests/test_<old_id>.py`) is now incorrect
     against current data, move it to `tests/superseded/` rather
     than deleting it.

7. **Run the full suite.**
   ```bash
   python -m pytest tests/
   python -m pytest tests/superseded/   # optional, to see what changed
   ```

8. **Commit with citation.**
   ```
   git add CLAIM_TABLE.json tests/test_<new_id>.py
   git commit -m "Update <claim_id> -> <new_id>: <one-line reason>

   Source: <citation / DOI / commit hash>
   Update reason: <new_evidence | error_correction | scope_refinement | falsification_partial>

   Prior version preserved at id <old_id>, marked current=false."
   ```

9. **If the new test fails:** do not commit the new claim as
   `current: true`. Instead:
   - log a draft entry under `predictions/drafts/` with the
     conflict documented
   - file a GitHub issue with the contradiction
   - keep the prior version `current: true`
   - the contradiction is itself part of the falsifiable record

---

## Example walk-through

> **Trigger.** A 2026 paper reports new measurement of <quantity> at
> <new value>, contradicting the value claim C42 was based on.
>
> **Steps.**
>
> 1. Trigger identified: arXiv:2603.NNNNN.
> 2. C42 is affected: it was based on the pre-2026 measurement.
> 3. Update reason: `new_evidence`.
> 4. New entry `C42_v2`:
>    - `claim`: revised statement with new measurement
>    - `probability_estimate`: updated based on new data
>    - `current: true`
>    - `supersedes: C42`
>    - `update_reason: new_evidence`
>    - `update_source: arXiv:2603.NNNNN`
> 5. Old entry C42:
>    - `current: false`
>    - `superseded_by: C42_v2`
> 6. New test `tests/test_C42_v2.py` validates C42_v2 against
>    the new measurement; old test moved to
>    `tests/superseded/test_C42.py`.
> 7. Full suite passes.
> 8. Commit.

---

## What this procedure protects

- **Track-record integrity.** A future audit can see every revision
  and its evidence basis.
- **Learning trace.** A reader can reconstruct how the repo's
  understanding converged.
- **Sycophancy detection.** Updates without an `update_source` are
  visible as suspicious in git history.
- **Cross-model auditability.** A different model can independently
  verify each update against the cited source.

---

## What this procedure does not promise

- It does not guarantee the new claim is correct. It only guarantees
  the *update* is documented and reversible.
- It does not adjudicate between contradictory sources. When sources
  conflict, the procedure keeps the prior version current and logs
  the contradiction; resolution requires further evidence.
