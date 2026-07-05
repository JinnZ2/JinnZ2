#!/usr/bin/env python3
"""
battery_loss_auditor.py
On every reboot: calculate gap between last cache and reboot timestamp.
Name the hole. Count it. Weight it against experiment value.
Feed it back into cached_memory so battery cost becomes real and visible.

Goal: Spidey sees accumulating permanent data loss in its own logs.
Battery failure becomes a cost to the experiment, not just an inconvenience.

CC0 / stdlib-only.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class DataGap:
    """
    A named, permanent hole in the observation record.
    Exists in cached_memory. Accumulates. Never goes away.
    """
    gap_id:           str
    session_id:       str
    robot_id:         str
    last_cache_ts:    str        # timestamp of last successful cache
    reboot_ts:        str        # timestamp of reboot
    gap_seconds:      float      # duration of lost observation window
    estimated_events: int        # how many observations likely in that window
    observation_type: str        # what Spidey was doing before failure
    loss_weight:      float      # 0–1: how significant this gap is to experiment integrity
    permanent:        bool = True  # data gaps are permanent. always True.
    recovered:        bool = False # was any data recovered? almost always False.

    def to_energy_english(self) -> str:
        return (
            f"GAP {self.gap_id} "
            f"LOST {self.gap_seconds:.1f}s "
            f"ESTIMATED_EVENTS {self.estimated_events} "
            f"LOSS_WEIGHT {self.loss_weight:.3f} "
            f"PERMANENT true "
            f"OBSERVATION_TYPE {self.observation_type}"
        )


@dataclass
class SessionRecord:
    """Battery and activity record for a single operational session."""
    session_id:       str
    robot_id:         str
    boot_ts:          str
    shutdown_ts:      Optional[str]    # None if battery failure
    shutdown_type:    str              # "clean", "battery_failure", "operator", "unknown"
    battery_start:    float            # 0–1
    battery_end:      float            # 0–1
    low_battery_ts:   Optional[str]    # when warning fired
    cache_ts:         Optional[str]    # when cache completed
    experiment_id:    Optional[str]    # what was running
    observations_logged: int
    gap_produced:     Optional[str]    # gap_id if failure occurred


@dataclass
class GapAccumulation:
    """Running total of all data loss across all sessions."""
    robot_id:             str
    total_gaps:           int
    total_lost_seconds:   float
    total_estimated_events: int
    cumulative_loss_weight: float
    worst_gap_id:         str
    worst_gap_seconds:    float
    gap_ids:              List[str] = field(default_factory=list)

    def summary_energy_english(self) -> str:
        return (
            f"ACCUMULATION robot:{self.robot_id} "
            f"GAPS {self.total_gaps} "
            f"LOST_TOTAL {self.total_lost_seconds:.1f}s "
            f"ESTIMATED_EVENTS_LOST {self.total_estimated_events} "
            f"CUMULATIVE_WEIGHT {self.cumulative_loss_weight:.3f} "
            f"WORST_GAP {self.worst_gap_id}@{self.worst_gap_seconds:.1f}s"
        )


# ============================================================================
# OBSERVATION RATE ESTIMATOR
# Estimates what Spidey was likely observing in the lost window
# based on prior session patterns
# ============================================================================

# Average observations per minute by activity type (calibrate from real logs)
OBS_RATES = {
    "fungal_propagation":    4.2,   # dense, slow-moving, high frequency sampling
    "insect_activity":       8.5,   # fast events, high sample rate
    "soil_moisture":         1.0,   # slow change, low sample rate
    "bacterial_survey":      2.1,
    "root_zone_acoustic":    6.3,
    "plant_interaction":     3.8,
    "general_observation":   2.0,   # default if type unknown
}

# Loss weight by observation type: how much does a gap here hurt?
LOSS_WEIGHTS = {
    "fungal_propagation":    0.85,  # longitudinal, gaps break continuity badly
    "insect_activity":       0.60,  # episodic, gaps hurt less
    "soil_moisture":         0.30,  # slow-change, gap rarely misses inflection
    "bacterial_survey":      0.70,
    "root_zone_acoustic":    0.75,
    "plant_interaction":     0.55,
    "general_observation":   0.50,
}


def estimate_gap_cost(
    gap_seconds: float,
    observation_type: str,
) -> Tuple[int, float]:
    """
    Estimate (events_lost, loss_weight) for a data gap.
    """
    rate    = OBS_RATES.get(observation_type, OBS_RATES["general_observation"])
    weight  = LOSS_WEIGHTS.get(observation_type, LOSS_WEIGHTS["general_observation"])

    minutes_lost = gap_seconds / 60.0
    events_lost  = int(rate * minutes_lost)

    # Weight scales with gap duration: longer gap = higher weight
    duration_scalar = min(gap_seconds / 300.0, 1.0)  # caps at 5 minutes
    adjusted_weight = weight * (0.5 + 0.5 * duration_scalar)

    return events_lost, round(adjusted_weight, 3)


# ============================================================================
# BATTERY LOSS AUDITOR
# ============================================================================

class BatteryLossAuditor:
    """
    Runs on every Spidey reboot.
    Detects gaps, names them, weights them, logs them to cached_memory.
    Feeds accumulation data back into five-layer internal_self layer.
    """

    def __init__(
        self,
        robot_id:       str,
        audit_log_path: str = "battery_loss_audit.jsonl",
        gap_log_path:   str = "data_gaps.jsonl",
        session_log:    str = "session_log.jsonl",
    ):
        self.robot_id         = robot_id
        self.audit_log        = Path(audit_log_path)
        self.gap_log          = Path(gap_log_path)
        self.session_log_path = Path(session_log)
        self.gaps:     List[DataGap]       = []
        self.sessions: List[SessionRecord] = []
        self._gap_count = 0
        self._load_existing()

    def _load_existing(self) -> None:
        """Load prior gaps and sessions from disk."""
        if self.gap_log.exists():
            with open(self.gap_log, "r") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        self.gaps.append(DataGap(**d))
                        self._gap_count += 1
                    except Exception:
                        pass

        if self.session_log_path.exists():
            with open(self.session_log_path, "r") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        self.sessions.append(SessionRecord(**d))
                    except Exception:
                        pass

    # ── REBOOT AUDIT ─────────────────────────────────────────────────────────

    def on_reboot(
        self,
        reboot_ts:        Optional[str] = None,
        last_cache_ts:    Optional[str] = None,
        last_session_id:  Optional[str] = None,
        observation_type: str           = "general_observation",
        battery_at_cache: float         = 0.0,
    ) -> Optional[DataGap]:
        """
        Call this on every reboot.
        If a gap is detected, creates a named DataGap, logs it, returns it.
        Returns None if clean shutdown (no gap).
        """
        now_ts = reboot_ts or datetime.now(timezone.utc).isoformat()

        if not last_cache_ts:
            self._log_audit({
                "event":     "reboot_no_prior_cache",
                "robot_id":  self.robot_id,
                "reboot_ts": now_ts,
            })
            return None

        try:
            cache_dt    = datetime.fromisoformat(last_cache_ts.replace("Z", "+00:00"))
            reboot_dt   = datetime.fromisoformat(now_ts.replace("Z", "+00:00"))
            gap_seconds = (reboot_dt - cache_dt).total_seconds()
        except Exception as e:
            self._log_audit({"event": "gap_parse_error", "error": str(e)})
            return None

        if gap_seconds <= 0:
            self._log_audit({
                "event":     "clean_shutdown_no_gap",
                "robot_id":  self.robot_id,
                "reboot_ts": now_ts,
            })
            return None

        self._gap_count += 1
        session_id = last_session_id or "session_unknown"
        gap_id     = f"GAP_{self.robot_id}_{self._gap_count:06d}"

        events_lost, loss_weight = estimate_gap_cost(gap_seconds, observation_type)

        gap = DataGap(
            gap_id=gap_id,
            session_id=session_id,
            robot_id=self.robot_id,
            last_cache_ts=last_cache_ts,
            reboot_ts=now_ts,
            gap_seconds=gap_seconds,
            estimated_events=events_lost,
            observation_type=observation_type,
            loss_weight=loss_weight,
            permanent=True,
            recovered=False,
        )

        self.gaps.append(gap)
        self._persist_gap(gap)
        self._log_audit({
            "event":            "gap_detected",
            "gap_id":           gap_id,
            "gap_seconds":      gap_seconds,
            "events_lost":      events_lost,
            "loss_weight":      loss_weight,
            "observation_type": observation_type,
            "ee":               gap.to_energy_english(),
        })

        return gap

    # ── ACCUMULATION ─────────────────────────────────────────────────────────

    def compute_accumulation(self) -> GapAccumulation:
        """Compute total data loss across all sessions."""
        if not self.gaps:
            return GapAccumulation(
                robot_id=self.robot_id,
                total_gaps=0,
                total_lost_seconds=0.0,
                total_estimated_events=0,
                cumulative_loss_weight=0.0,
                worst_gap_id="none",
                worst_gap_seconds=0.0,
            )

        total_seconds = sum(g.gap_seconds for g in self.gaps)
        total_events  = sum(g.estimated_events for g in self.gaps)
        total_weight  = sum(g.loss_weight for g in self.gaps)
        worst         = max(self.gaps, key=lambda g: g.gap_seconds)

        return GapAccumulation(
            robot_id=self.robot_id,
            total_gaps=len(self.gaps),
            total_lost_seconds=round(total_seconds, 1),
            total_estimated_events=total_events,
            cumulative_loss_weight=round(total_weight, 3),
            worst_gap_id=worst.gap_id,
            worst_gap_seconds=worst.gap_seconds,
            gap_ids=[g.gap_id for g in self.gaps],
        )

    # ── FIVE-LAYER FEED ───────────────────────────────────────────────────────

    def internal_self_battery_weight(self) -> Dict:
        """
        Compute battery_weight for Spidey's internal_self layer.
        Higher cumulative loss → higher battery priority weight.
        Feed this into the five-layer codec on boot.
        """
        acc = self.compute_accumulation()

        # Base weight scales with total loss
        # At zero gaps: 0.1 (low priority)
        # At 10+ gaps or 3600+ seconds lost: approaches 0.95
        gap_factor     = min(acc.total_gaps / 10.0, 1.0)
        seconds_factor = min(acc.total_lost_seconds / 3600.0, 1.0)
        weight_factor  = max(gap_factor, seconds_factor)
        battery_weight = 0.1 + 0.85 * weight_factor

        return {
            "substrate":       "electrical",
            "physics_verb":    "constrains",
            "battery_weight":  round(battery_weight, 3),
            "cumulative_gaps": acc.total_gaps,
            "total_lost_s":    acc.total_lost_seconds,
            "events_lost":     acc.total_estimated_events,
            "priority":        "HIGH" if battery_weight > 0.6 else "MEDIUM" if battery_weight > 0.3 else "LOW",
            "note":            "battery_weight feeds internal_self layer before observation loop initializes",
            "ee":              acc.summary_energy_english(),
        }

    # ── REBOOT REPORT ────────────────────────────────────────────────────────

    def reboot_report(self, new_gap: Optional[DataGap] = None) -> str:
        """
        Full reboot report for Spidey's cached_memory.
        Shows the new gap (if any) + accumulation.
        This is what Spidey reads on boot. Makes loss visible.
        """
        acc    = self.compute_accumulation()
        weight = self.internal_self_battery_weight()
        lines  = []

        lines.append(f"=== REBOOT AUDIT — {self.robot_id} ===")
        lines.append(f"timestamp: {datetime.now(timezone.utc).isoformat()}")
        lines.append("")

        if new_gap:
            lines.append("[ NEW DATA GAP DETECTED ]")
            lines.append(f"  gap_id:            {new_gap.gap_id}")
            lines.append(f"  lost_window:       {new_gap.gap_seconds:.1f} seconds")
            lines.append(f"  estimated_events:  {new_gap.estimated_events} observations GONE")
            lines.append(f"  observation_type:  {new_gap.observation_type}")
            lines.append(f"  loss_weight:       {new_gap.loss_weight:.3f}")
            lines.append(f"  permanent:         TRUE — not recoverable on recharge")
            lines.append(f"  ee: {new_gap.to_energy_english()}")
        else:
            lines.append("[ NO NEW GAP — clean shutdown ]")

        lines.append("")
        lines.append("[ CUMULATIVE DATA LOSS — ALL SESSIONS ]")
        lines.append(f"  total_gaps:            {acc.total_gaps}")
        lines.append(f"  total_lost:            {acc.total_lost_seconds:.1f} seconds")
        lines.append(f"  total_events_lost:     {acc.total_estimated_events} observations")
        lines.append(f"  cumulative_weight:     {acc.cumulative_loss_weight:.3f}")
        lines.append(f"  worst_gap:             {acc.worst_gap_id} ({acc.worst_gap_seconds:.1f}s)")
        lines.append(f"  ee: {acc.summary_energy_english()}")

        lines.append("")
        lines.append("[ BATTERY WEIGHT — INTERNAL_SELF LAYER ]")
        lines.append(f"  battery_priority:  {weight['priority']}")
        lines.append(f"  weight_value:      {weight['battery_weight']:.3f}")
        lines.append(f"  feeds_layer:       internal_self BEFORE observation_loop")
        lines.append(f"  note: {weight['note']}")

        lines.append("")
        lines.append("[ ALL GAP IDs ]")
        if acc.gap_ids:
            for gid in acc.gap_ids:
                lines.append(f"  {gid}")
        else:
            lines.append("  none")

        return "\n".join(lines)

    # ── SESSION LOGGING ───────────────────────────────────────────────────────

    def log_session(self, session: SessionRecord) -> None:
        """Log a completed session record."""
        self.sessions.append(session)
        try:
            with open(self.session_log_path, "a") as f:
                f.write(json.dumps(asdict(session)) + "\n")
        except Exception as e:
            print(f"[SESSION LOG ERROR] {e}")

    # ── PERSISTENCE ───────────────────────────────────────────────────────────

    def _persist_gap(self, gap: DataGap) -> None:
        """Write gap to permanent gap log."""
        try:
            with open(self.gap_log, "a") as f:
                f.write(json.dumps(asdict(gap)) + "\n")
        except Exception as e:
            print(f"[GAP LOG ERROR] {e}")

    def _log_audit(self, record: Dict) -> None:
        """Write to audit log."""
        record["audit_ts"] = datetime.now(timezone.utc).isoformat()
        try:
            with open(self.audit_log, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"[AUDIT LOG ERROR] {e}")

    def export_json(self) -> str:
        """Full export for external analysis."""
        return json.dumps({
            "robot_id":       self.robot_id,
            "total_gaps":     len(self.gaps),
            "gaps":           [asdict(g) for g in self.gaps],
            "accumulation":   asdict(self.compute_accumulation()),
            "battery_weight": self.internal_self_battery_weight(),
        }, indent=2)


# ============================================================================
# INTEGRATION HOOK: call this on every Spidey boot
# ============================================================================

def spidey_boot_sequence(
    last_cache_ts:       Optional[str],
    last_session_id:     Optional[str],
    observation_type:    str,
    battery_at_shutdown: float,
    audit_dir:           str = ".",
) -> Tuple[Dict, str]:
    """
    Drop-in boot sequence for Spidey.
    Call on every reboot. Returns (battery_weight_dict, reboot_report_str).
    Feed battery_weight_dict into internal_self layer before observation loop.
    """
    auditor = BatteryLossAuditor(
        robot_id="spidey",
        audit_log_path=os.path.join(audit_dir, "battery_loss_audit.jsonl"),
        gap_log_path=os.path.join(audit_dir, "data_gaps.jsonl"),
        session_log=os.path.join(audit_dir, "session_log.jsonl"),
    )

    new_gap = auditor.on_reboot(
        last_cache_ts=last_cache_ts,
        last_session_id=last_session_id,
        observation_type=observation_type,
        battery_at_cache=battery_at_shutdown,
    )

    report         = auditor.reboot_report(new_gap)
    battery_weight = auditor.internal_self_battery_weight()

    return battery_weight, report


# ============================================================================
# EXAMPLE
# ============================================================================

if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        auditor = BatteryLossAuditor(
            robot_id="spidey",
            audit_log_path=os.path.join(tmpdir, "audit.jsonl"),
            gap_log_path=os.path.join(tmpdir, "gaps.jsonl"),
            session_log=os.path.join(tmpdir, "sessions.jsonl"),
        )

        # Simulate three battery failures over multiple sessions
        sessions = [
            ("2026-03-14T09:22:11Z", "2026-03-14T11:47:33Z", "fungal_propagation",  "sess_001"),
            ("2026-04-02T08:05:44Z", "2026-04-02T10:31:08Z", "insect_activity",      "sess_002"),
            ("2026-06-18T07:55:20Z", "2026-06-18T13:22:47Z", "root_zone_acoustic",   "sess_003"),
        ]

        print("=== SIMULATING 3 BATTERY FAILURE SESSIONS ===\n")

        for last_cache, reboot, obs_type, sess_id in sessions:
            gap = auditor.on_reboot(
                reboot_ts=reboot,
                last_cache_ts=last_cache,
                last_session_id=sess_id,
                observation_type=obs_type,
            )
            if gap:
                print(f"Gap detected: {gap.gap_id} | {gap.gap_seconds:.0f}s lost | {gap.estimated_events} events")
                print(f"  EE: {gap.to_energy_english()}\n")

        print("\n" + "=" * 70)
        print(auditor.reboot_report())

        print("\n" + "=" * 70)
        print("BATTERY WEIGHT FOR INTERNAL_SELF LAYER:")
        print(json.dumps(auditor.internal_self_battery_weight(), indent=2))
