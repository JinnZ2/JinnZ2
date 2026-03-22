#!/usr/bin/env bash
# micro_module.sh — Generate a Micro-Module template
# Creates a teach-in-5-to-15-minutes module following the format
# from micro-modules.md: Goal -> Steps -> Materials -> Success -> Teach next.
#
# Usage:
#   ./micro_module.sh                    # interactive
#   ./micro_module.sh "Seed Keep"        # with title

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT="${SCRIPT_DIR}/micro-modules.md"
TIMESTAMP=$(date -u +"%Y-%m-%d")

echo "Micro-Module Generator"
echo "======================"
echo ""
echo "Format: Goal -> Steps (3-7) -> Materials (tiny) -> Success signs -> Who to teach next"
echo ""

# Title
if [[ $# -ge 1 ]]; then
    TITLE="$1"
else
    read -rp "Module title: " TITLE
fi

if [[ -z "$TITLE" ]]; then
    echo "Title required."
    exit 1
fi

# Goal
echo ""
read -rp "Goal (one sentence — what does the learner achieve?): " GOAL

# Steps
echo ""
echo "Steps (3-7 steps, one per line, empty line to finish):"
STEPS=""
step_num=1
while [[ $step_num -le 7 ]]; do
    read -rp "  ${step_num}. " step
    [[ -z "$step" ]] && break
    STEPS="${STEPS}${step_num}. ${step}\n"
    ((step_num++))
done

if [[ -z "$STEPS" ]]; then
    echo "At least one step required."
    exit 1
fi

# Materials
echo ""
read -rp "Materials (tiny list, comma-separated): " MATERIALS

# Success signs
echo ""
read -rp "Signs of success (how do you know it worked?): " SUCCESS

# Teach next
echo ""
echo "Who to teach next (two names — the module must propagate):"
read -rp "  Person 1: " TEACH1
read -rp "  Person 2: " TEACH2

# Write the module
{
    echo ""
    echo "## ${TITLE}"
    echo "Goal: ${GOAL}"
    echo ""
    echo "Steps:"
    echo -e "${STEPS}"
    echo "Materials: ${MATERIALS}"
    echo ""
    echo "Success: ${SUCCESS}"
    echo ""
    echo "Teach next: ${TEACH1}, ${TEACH2}"
    echo ""
    echo "_Added: ${TIMESTAMP}_"
} >> "$OUTPUT"

echo ""
echo "Module appended to micro-modules.md"
echo ""
echo "  Title: ${TITLE}"
echo "  Goal: ${GOAL}"
echo "  Steps: $((step_num - 1))"
echo "  Propagates to: ${TEACH1}, ${TEACH2}"
echo ""
echo "The module must be teachable in 5-15 minutes."
echo "If it takes longer, break it into smaller modules."
