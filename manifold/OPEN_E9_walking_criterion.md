# OPEN E9 — WALKING vs INTERMITTENT criterion

Status: OPEN / EMPIRICAL
Do not patch until E9 is run. Resolution requires a new log entry that
supersedes 03efe4e41e61, plus a versioned change. Never an untracked edit.

---

## First Real Log Entry

```
id           03efe4e41e61
subject      residual.WALKING_criterion
kind         band_only   (same digest, different band -- real divergence)
digest       n3-gaps:-1,0,+2
SPEC_intent  INTERMITTENT
BEHAVIOR     WALKING
status       OPEN
```

The trigger: a series of n=3 band-differences with values [-1, 0, +2].
The current criterion (`all(d >= diffs[0])`) passes this as WALKING because
every diff is >= the first diff (-1). The spec intent for this series was
INTERMITTENT.

This is logged, not patched. The entry is the artifact.

---

## What E9 Must Answer

E9: WALKING vs INTERMITTENT -- report BOTH error rates.

A criterion change fixes one error by introducing the other. Reporting only
the fix is reporting only one side of the tradeoff. E9 is not runnable until
we have a noise scale from real divergence histories (E16). A synthetic sweep
run before E16 reports false-alarm and miss rates against a made-up baseline,
which is itself a fabrication.

### Synthetic arm (runnable now)

Sweep candidate WALKING criteria over n = 3..30 synthetic series:
- current: `all(d >= diffs[0])`
- strict consecutive: `all(diffs[i+1] >= diffs[i] for i in range(n-1))`
- slope-sign: sign of linear regression slope
- threshold: `|diffs[-1] - diffs[0]| > k` for some k

For each candidate: what fraction of truly-intermittent series are
mis-classified WALKING (false alarm)? What fraction of truly-walking
series are mis-classified INTERMITTENT (miss)?

Report both rates. Do not pick the criterion with the lowest false-alarm
rate alone.

### Field arm (blocked on E16)

Only real divergence histories can set the noise scale. A series that looks
WALKING in synthetic data may be noise at the scale of real instrument drift.
E16 (log becomes a baseline) must register before E9 can interpret field data.

---

## Resolution Rule

1. Run E9 synthetic arm. Record both error rates in this file.
2. Wait for E16 (field histories). Re-run with real noise scale.
3. Select criterion. Write a new divlog.py version with the change.
4. Append a new log entry:
   ```
   supersedes   03efe4e41e61
   subject      residual.WALKING_criterion
   kind         band_only
   digest       <new criterion string>
   note         E9 resolved: <criterion chosen>, FA=<rate>, miss=<rate>
   ```
5. Commit entry + code change together.

The old entry 03efe4e41e61 stays in the log. Append-only.
