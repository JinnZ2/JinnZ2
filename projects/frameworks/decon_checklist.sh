#!/usr/bin/env bash
# decon_checklist.sh — Western Framework Decontamination Workflow
# Interactive walkthrough of the 6-step process from Decon.md.
# Logs each step's findings to a timestamped file.
#
# Usage: ./decon_checklist.sh [framework-name]

set -euo pipefail

FRAMEWORK="${1:-unnamed_framework}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H%M%SZ")
LOGFILE="decon_${FRAMEWORK// /_}_${TIMESTAMP}.log"

log() {
    echo "$1" | tee -a "$LOGFILE"
}

prompt_step() {
    local step_num="$1"
    local step_name="$2"
    local goal="$3"
    shift 3

    log ""
    log "============================================"
    log "STEP ${step_num}: ${step_name}"
    log "Goal: ${goal}"
    log "============================================"

    for question in "$@"; do
        log ""
        log "  Q: ${question}"
        echo -n "  A: "
        read -r answer
        log "  A: ${answer}"
    done

    log ""
    log "  Step ${step_num} complete — $(date -u +"%H:%M:%S UTC")"
}

log "DECONTAMINATION AUDIT — ${FRAMEWORK}"
log "Started: ${TIMESTAMP}"
log ""

prompt_step 1 "PRELIMINARY AUDIT" \
    "Identify embedded assumptions, biases, and structural defaults." \
    "What are the framework's core principles/metrics/procedures?" \
    "Which values are prioritized — individual or collective?" \
    "What assumptions about causality, control, or efficiency are present?" \
    "Are there hidden incentives, hierarchies, or dependencies?" \
    "Which elements conflict with Energy Code (transparency, measurability, cyclical alignment, generational sustainability)?"

prompt_step 2 "ENERGY CODE FILTERING" \
    "Test every component against the Energy Code." \
    "Energy Accounting — are benefits and costs clear? Hidden consequences?" \
    "Natural Alignment — does this respect cycles, limits, rhythms?" \
    "Measurable Outcomes — can results be verified without artificial shortcuts?" \
    "Seven Generations — would this enhance or harm long-term sustainability?" \
    "No Hidden Costs — are obligations, payments, or dependency structures introduced?"

prompt_step 3 "NEUTRALIZE EXTRACTIVE PATTERNS" \
    "Remove control dynamics or power-extracting mechanisms." \
    "Where are the hierarchies? How can 'expert vs subject' become 'co-observer'?" \
    "What reward structures privilege the framework owner over the system's wellbeing?" \
    "Are there promises of 'fast results' that violate natural cycles?"

prompt_step 4 "TRANSLATE TO CULTURAL COMPATIBILITY" \
    "Convert concepts into a form that safely interfaces with other knowledge systems." \
    "Where can linear causality be replaced with cyclical or networked logic?" \
    "Which rigid metrics can become energy-informed indicators (quality, resilience, relational harmony)?" \
    "Can this be applied modularly — enhancing other systems without dominating them?"

prompt_step 5 "INDEPENDENT VERIFICATION" \
    "Ensure neutrality and authenticity." \
    "How does this hold up against indigenous knowledge or other cultural frameworks?" \
    "How does this hold up against empirical observation?" \
    "Any signs of unintended dependency, energy drain, or manipulation?"

prompt_step 6 "CONTINUOUS FEEDBACK" \
    "Keep the system dynamic and self-correcting." \
    "What review cycle makes sense (monthly, quarterly, seasonal)?" \
    "How will you track energy flow — enhancement vs depletion?" \
    "How will you monitor participant autonomy and independence?" \
    "How will you check alignment with natural rhythms over time?"

log ""
log "============================================"
log "DECONTAMINATION COMPLETE"
log "Finished: $(date -u +"%Y-%m-%dT%H%M%SZ")"
log "Log saved: ${LOGFILE}"
log "============================================"
log ""
log "Next: feed outputs back into the cycle. The work is never done."
