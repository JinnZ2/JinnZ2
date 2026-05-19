"""
resonance_checkpoint.py — Cross-Domain Coupling Detector

Implements the safety checklist from resonance-checkpoint.md.
Monitors sensor readings across domains (thermal, vibration, acoustic, EM, optical)
and flags coupling events when thresholds are exceeded.

Usage:
    python resonance_checkpoint.py                  # interactive monitoring
    python resonance_checkpoint.py --baseline 120   # record 120s baseline
    python resonance_checkpoint.py --review LOG.csv # review a log file

No external dependencies — standard library only.
Sensor data entered manually or piped from instruments.
"""

import csv
import sys
import os
from datetime import datetime, timezone

DOMAINS = ["thermal", "vibration", "acoustic", "em", "optical", "power"]

THRESHOLDS = {
    "thermal": {
        "unit": "deg C above baseline",
        "warning": 3.0,
        "critical": 5.0,
        "note": "unexpected local temp rise",
    },
    "vibration": {
        "unit": "x baseline RMS",
        "warning": 1.5,
        "critical": 2.0,
        "note": "sudden acceleration spike",
    },
    "acoustic": {
        "unit": "new harmonic peaks",
        "warning": 1,
        "critical": 3,
        "note": "sharp spectral peaks not in drive signal",
    },
    "em": {
        "unit": "x ambient gauss",
        "warning": 1.5,
        "critical": 2.0,
        "note": "unexpected induced voltages",
    },
    "optical": {
        "unit": "events (flicker/flash)",
        "warning": 1,
        "critical": 2,
        "note": "flicker, glint, or blooming",
    },
    "power": {
        "unit": "% above expected draw",
        "warning": 15,
        "critical": 30,
        "note": "persistent draw increasing while output stable",
    },
}

SAFETY_REMINDERS = [
    "HAVE AN EMERGENCY SHUT OFF SWITCH WITHIN REACH",
    "Clear workspace of flammables and loose cables",
    "PPE: safety glasses, nitrile gloves, hearing protection if >85 dB",
    "Use low initial energy — ramp gradually",
    "Never leave an active experiment unattended",
]


def print_safety():
    print("\n" + "=" * 50)
    print("SAFETY PREREQUISITES")
    print("=" * 50)
    for r in SAFETY_REMINDERS:
        print(f"  * {r}")
    print("=" * 50)


def record_baseline():
    """Record baseline readings for each domain."""
    baselines = {}
    print("\nRecord baseline readings (2-5 min ambient):")
    for domain in DOMAINS:
        t = THRESHOLDS[domain]
        val = input(f"  {domain} baseline ({t['unit']}): ").strip()
        try:
            baselines[domain] = float(val) if val else 0.0
        except ValueError:
            baselines[domain] = 0.0
    return baselines


def check_reading(domain, value, baseline):
    """Check a reading against thresholds. Returns alert level."""
    t = THRESHOLDS[domain]

    if domain in ("acoustic", "optical"):
        delta = value
    elif domain == "power":
        if baseline > 0:
            delta = ((value - baseline) / baseline) * 100
        else:
            delta = value
    elif domain in ("thermal",):
        delta = value - baseline
    else:
        delta = value / baseline if baseline > 0 else value

    if delta >= t["critical"]:
        return "CRITICAL", delta, t
    elif delta >= t["warning"]:
        return "WARNING", delta, t
    return "OK", delta, t


def interactive_monitor():
    """Run interactive monitoring session."""
    print_safety()

    confirm = input("\nAll safety checks passed? [y/n]: ").strip().lower()
    if confirm != "y":
        print("Complete safety prerequisites before proceeding.")
        return

    baselines = record_baseline()
    logfile = f"resonance_log_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}.csv"

    with open(logfile, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "event_id", "datetime_utc", "domain", "reading",
            "baseline", "delta", "level", "action", "notes"
        ])

    event_counter = 1
    materials = input("\nMaterials & geometry (short note): ").strip()
    drive_type = input("Drive type: ").strip()

    print("\nMonitoring active. Enter readings per domain.")
    print("Type 'q' to end, 's' for status, 'all' to enter all domains at once.")
    print()

    readings_log = []

    while True:
        cmd = input("Domain [thermal/vibration/acoustic/em/optical/power/all/s/q]: ").strip().lower()

        if cmd == "q":
            break
        if cmd == "s":
            print(f"\n  Entries logged: {len(readings_log)}")
            print(f"  Log file: {logfile}")
            alerts = sum(1 for r in readings_log if r["level"] != "OK")
            print(f"  Alerts triggered: {alerts}")
            continue

        domains_to_check = DOMAINS if cmd == "all" else [cmd]
        if cmd != "all" and cmd not in DOMAINS:
            print(f"  Unknown domain. Options: {', '.join(DOMAINS)}")
            continue

        cascade_alerts = []

        for domain in domains_to_check:
            val_str = input(f"  {domain} reading: ").strip()
            if not val_str:
                continue
            try:
                value = float(val_str)
            except ValueError:
                print("  Enter a number.")
                continue

            level, delta, t = check_reading(domain, value, baselines.get(domain, 0))
            notes = ""
            action = "continue"

            if level == "CRITICAL":
                print(f"\n  *** CRITICAL — {domain}: {t['note']} ***")
                print(f"      Delta: {delta:.2f} {t['unit']} (threshold: {t['critical']})")
                print(f"      ACTION: CUT DRIVE POWER. Keep sensors live 30-120s.")
                action = "power_cut"
                cascade_alerts.append(domain)
            elif level == "WARNING":
                print(f"  ! WARNING — {domain}: {t['note']}")
                print(f"    Delta: {delta:.2f} {t['unit']} (threshold: {t['warning']})")
                action = "monitor_closely"

            notes_input = input(f"  Notes for {domain}: ").strip() if level != "OK" else ""
            entry = {
                "event_id": f"CR{datetime.now().year}-{event_counter:03d}",
                "time": datetime.now(timezone.utc).isoformat(),
                "domain": domain,
                "reading": value,
                "baseline": baselines.get(domain, 0),
                "delta": delta,
                "level": level,
                "action": action,
                "notes": notes_input,
            }
            readings_log.append(entry)

            with open(logfile, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    entry["event_id"], entry["time"], domain,
                    value, baselines.get(domain, 0), f"{delta:.2f}",
                    level, action, notes_input,
                ])

            event_counter += 1

        # cascade detection
        if len(cascade_alerts) >= 2:
            print("\n  ****************************************************")
            print("  MULTI-DOMAIN CASCADE DETECTED")
            print(f"  Domains: {', '.join(cascade_alerts)}")
            print("  ACTION: IMMEDIATE FULL POWER ISOLATION")
            print("  Ventilate if smoke. Maintain safe distance.")
            print("  Wait 10-30 minutes before approaching.")
            print("  ****************************************************\n")

    print(f"\nSession complete. Log saved: {logfile}")
    print(f"Total readings: {len(readings_log)}")
    alerts = [r for r in readings_log if r["level"] != "OK"]
    if alerts:
        print(f"Alerts: {len(alerts)}")
        for a in alerts:
            print(f"  [{a['level']}] {a['domain']}: {a['delta']:.2f} — {a['action']}")


def review_log(path):
    """Review a saved resonance log."""
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Reviewing: {path}")
    print(f"Entries: {len(rows)}\n")

    for row in rows:
        level = row.get("level", "OK")
        marker = "***" if level == "CRITICAL" else "!" if level == "WARNING" else " "
        print(f"  {marker} [{row['domain']}] {row['reading']} "
              f"(delta: {row['delta']}) — {level} — {row.get('notes', '')}")

    criticals = [r for r in rows if r.get("level") == "CRITICAL"]
    warnings = [r for r in rows if r.get("level") == "WARNING"]
    print(f"\nCritical: {len(criticals)}, Warnings: {len(warnings)}, OK: {len(rows) - len(criticals) - len(warnings)}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--review":
        review_log(sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == "--baseline":
        print_safety()
        baselines = record_baseline()
        print("\nBaselines recorded:")
        for k, v in baselines.items():
            print(f"  {k}: {v}")
    else:
        interactive_monitor()
