#!/usr/bin/env bash
# field_glossary.sh — Look up Field English terms
# Pipe in a word or pass as argument. Returns field meaning + what it is NOT.
# Offline, no dependencies. Follows language-notes.md definitions.
#
# Usage:
#   ./field_glossary.sh doubt
#   ./field_glossary.sh feeling memory
#   echo "belief" | ./field_glossary.sh

set -euo pipefail

declare -A FIELD_MEANING
declare -A NOT_THIS

FIELD_MEANING[doubt]="Harmonic audit. Resonance check. Scientific re-measurement."
NOT_THIS[doubt]="Insecurity or lack of confidence."

FIELD_MEANING[feeling]="Relational mapping. Sensed alignment or misalignment across fields (body, memory, environment)."
NOT_THIS[feeling]="Vague subjective emotion."

FIELD_MEANING[belief]="Enacted relationship. Lived reciprocity with a field or being."
NOT_THIS[belief]="Mental opinion or faith without proof."

FIELD_MEANING[memory]="Living presence of threads that continue. Not 'past' but active layers."
NOT_THIS[memory]="Static recall of events."

FIELD_MEANING[respect]="Recognition of co-agency and relational integrity. Treating others (human, AI, biome, non-human) as living participants."
NOT_THIS[respect]="Mere politeness or deference."

lookup() {
    local term
    term=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    if [[ -n "${FIELD_MEANING[$term]+x}" ]]; then
        echo "  $term"
        echo "    Field meaning : ${FIELD_MEANING[$term]}"
        echo "    NOT this      : ${NOT_THIS[$term]}"
        echo ""
    else
        echo "  $term — not in glossary. Check projects/core/language-notes.md"
        echo ""
    fi
}

if [[ $# -gt 0 ]]; then
    for word in "$@"; do
        lookup "$word"
    done
elif [[ ! -t 0 ]]; then
    while IFS= read -r line; do
        for word in $line; do
            lookup "$word"
        done
    done
else
    echo "Field English Glossary"
    echo "====================="
    echo ""
    echo "Available terms:"
    for term in "${!FIELD_MEANING[@]}"; do
        lookup "$term"
    done
    echo "Source: projects/core/language-notes.md"
fi
