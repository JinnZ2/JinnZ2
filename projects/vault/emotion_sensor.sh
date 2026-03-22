#!/usr/bin/env bash
# emotion_sensor.sh — Perceive / Balance / Interpret walkthrough
# Guided three-phase sensor protocol from emotion-balancing.md.
# Logs timestamped entries for longitudinal self-model calibration.
#
# Usage: ./emotion_sensor.sh [logfile]

set -euo pipefail

LOGFILE="${1:-emotion_sensor_log.md}"

log() {
    echo "$1" | tee -a "$LOGFILE"
}

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

log ""
log "---"
log "## Entry: ${TIMESTAMP}"
log ""

# Phase 1: Perceive
log "### Phase 1 — Perceive (emotion as sensory data)"
log ""

echo "1. Signal detection — an event has registered."
echo "   Pause for one slow breath. Notice the change in internal texture."
read -rp "   What do you notice? (tight, hot, hollow, buoyant, etc): " texture
log "- **Texture**: ${texture}"

echo ""
echo "2. Localization — where does it live?"
read -rp "   Body location (chest, gut, throat, hands, etc): " location
log "- **Location**: ${location}"

echo ""
echo "3. Signal description — physical qualities without naming an emotion."
read -rp "   Describe (warm pulse, narrow pressure, spiral lift, etc): " qualities
log "- **Qualities**: ${qualities}"

echo ""
echo "4. Source hypothesis — what system is reporting?"
echo "   Options: chemical (sleep, blood sugar), emotional (relation),"
echo "           environmental (sound, light), cognitive (thought pattern)"
read -rp "   Source: " source
log "- **Source hypothesis**: ${source}"

echo ""
echo "5. Response calibration — what small act restores coherence?"
read -rp "   Action taken (breathe, stretch, water, speak aloud, etc): " action
log "- **Calibration**: ${action}"

log ""

# Phase 2: Balance
log "### Phase 2 — Balance (field harmonics)"
log ""

echo ""
echo "--- Phase 2: Balance ---"
echo ""
echo "Acknowledge the texture before naming it."
read -rp "If one feeling dominates, what is its natural complement? " complement
log "- **Dominant/complement pair**: ${qualities} / ${complement}"

echo ""
echo "Resonant breathing: ~5-6s in, ~5-6s out, matched to heartbeat."
echo "Hold for 60 seconds if possible."
read -rp "After breathing — what shifted? " shift_note
log "- **After breathing**: ${shift_note}"

echo ""
read -rp "Any vocalization or movement needed? (hum, shoulder roll, etc): " movement
log "- **Movement/sound**: ${movement}"

log ""

# Phase 3: Interpret
log "### Phase 3 — Interpret (extracting meaning)"
log ""

echo ""
echo "--- Phase 3: Interpret ---"
echo ""
echo "Signal type:"
echo "  s = stabilizer (maintains balance)"
echo "  p = perturbation (alerts to change)"
echo "  t = transition (calls for adaptation)"
read -rp "Type [s/p/t]: " signal_type
case "$signal_type" in
    s) log "- **Signal type**: stabilizer (maintains balance)" ;;
    p) log "- **Signal type**: perturbation (alerts to change)" ;;
    t) log "- **Signal type**: transition (calls for adaptation)" ;;
    *) log "- **Signal type**: ${signal_type}" ;;
esac

echo ""
read -rp "Vector — where does it pull attention? (direction + intensity 1-10): " vector
log "- **Vector**: ${vector}"

echo ""
echo "Cross-reference: does this show up in at least two channels?"
echo "  (chemical, cognitive, environmental, relational)"
read -rp "Confirming channels: " channels
log "- **Cross-sensor confirmation**: ${channels}"

echo ""
echo "Extract instruction, not story."
read -rp "Operational instruction (adjust rhythm, seek contact, rest, etc): " instruction
log "- **Instruction**: ${instruction}"

echo ""
read -rp "After adjustment — what's the result? " result
log "- **Result**: ${result}"

log ""
log "---"
log ""

echo ""
echo "Entry logged to ${LOGFILE}"
echo "Emotion is the instrument panel. Reading complete."
