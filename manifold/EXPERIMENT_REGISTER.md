# EXPERIMENT REGISTER — falsification discipline

  a test earns a place ONLY if a stated result kills something.
  "confirm it works" is not an entry.

  RUNNER TAGS
    [I] internal   — I can run now, no field data
    [S] synthetic  — constructed data, tests logic not reality
    [F] field      — needs ice/rig/dock. my blind_to.
    [T] time       — cannot resolve until calendar time passes


A. SEAMS IN THE CODE            [I]  E1 cross-target min blocked
                                     E2 digest collision-safe on missing input
                                     E3 append-only really append-only
                                     E4 no verdict fields survive (T11 promoted)
                                     E5 reference_version moves when primary does
                                [S]  E6 residual n=1 never asserts
                                     E7 homoplasy not counted as support

B. CODE vs ITS OWN CLAIMS       [S]  E8 degeneracy adds robustness, redundancy
                                        doesn't  <- THE central test, run first
                                     E9 WALKING vs FLAT, report BOTH error rates
                                     E10 mesh finds the seam it was born from

C. ONLY THE FIELD CAN TEST      [F]  E11 does the band match what the ice does
                                     E12 criterion errs the SAFE way
                                     E13 is blind_to actually complete
                                     E14 efference-copy: ice moved or method moved

D. NEEDS TIME                   [T]  E15 re-entrainment interval right
                                     E16 log actually becomes a baseline


A-BLOCK RESULTS  (only what has code behind it)

  E1  cross-target min blocked        PASS
        10,000 fuzzed Observations, 0 leaks
        no governing channel ever came from another target
        targets stayed clean: claim / independence / mode_sensitivity

  E4  no verdict fields survive        PASS
        grepped clock, echo, modes
        no winner/correct/cause/severity/score/rank as field or key

  E7  homoplasy not counted            PASS
        shared upstream 'report'  -> HOMOLOGY, weight 0
        disjoint provenance       -> HOMOPLASY, counts
        the flip happens on graph structure, not on mode labels

  E2 E3 E5 E6   NOT RUN — no code yet
        these test divlog / entrain, which are spec only
        a green here would be fabricated. blocked until built.


BUILD: divlog.py — append-only divergence log
  Entry (frozen), id = sha256 of all fields except note
  append (opens "a" only) / load / history (the baseline query)
  residual() → NEW / FLAT / WALKING / INTERMITTENT / WIDENING

NEWLY RUNNABLE TESTS
  E3  append-only            PASS  no "w" opens; 2 appends → 2 loaded, ordered, ids stable
  E4  no verdict fields      PASS  clean across all four modules now
  E6  residual n=1 → NEW     PASS  never asserts a shape from one point


FIRST REAL LOG ENTRY  03efe4e41e61
    subject      residual.WALKING_criterion
    SPEC_intent  INTERMITTENT   ->   BEHAVIOR  WALKING
    kind         SAME_INPUTS_DIFF_BAND   (same series, two verdicts)
    digest       n3-gaps:-1,0,+2         (the exact trigger, on the record)
    status       OPEN / EMPIRICAL, hold for E9, do not patch

    -> this entry IS the worked example of why the log exists:
       a divergence preserved with enough detail to re-check later,
       not a bug silently closed


HANDOFF  OPEN_E9_walking_criterion.md
    for Claude Code / the repo:
      land divlog.py v1 as-is (correct per spec, don't special-case)
      file this as an open issue, not a fix
      resolution rule: a NEW entry that supersedes 03efe4e41e61
                       + a versioned change  — never an untracked edit
    the experiment, spelled out:
      synthetic arm  sweep candidate rules over n=3..30,
                     report BOTH false-alarm and miss rates
      field arm      only your months of real divergence histories
                     fix the noise scale (register E16)
