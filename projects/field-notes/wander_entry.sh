#!/usr/bin/env bash
# wander_entry.sh — Quick capture for WANDER.md
# Appends a timestamped entry with optional tags.
# Designed for fast fragment capture — integrate later.
#
# Usage:
#   ./wander_entry.sh                          # interactive
#   ./wander_entry.sh "the idea" "tag1,tag2"   # one-shot
#   echo "quick thought" | ./wander_entry.sh   # piped

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WANDER="${SCRIPT_DIR}/WANDER.md"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_SHORT=$(date -u +"%Y-%m-%d")

append_entry() {
    local content="$1"
    local tags="${2:-}"

    {
        echo ""
        echo ""
        echo "## Entry: ${DATE_SHORT}"
        echo ""
        echo "${content}"
        if [[ -n "$tags" ]]; then
            echo ""
            echo "Tags: ${tags}"
        fi
        echo ""
        echo "_Captured: ${TIMESTAMP}_"
    } >> "$WANDER"

    echo "Logged to WANDER.md"
    echo "  ${content:0:60}$([ ${#content} -gt 60 ] && echo '...' || echo '')"
}

# one-shot mode
if [[ $# -ge 1 ]]; then
    append_entry "$1" "${2:-}"
    exit 0
fi

# piped mode
if [[ ! -t 0 ]]; then
    content=""
    while IFS= read -r line; do
        content="${content}${line}\n"
    done
    append_entry "$(echo -e "$content")" ""
    exit 0
fi

# interactive mode
echo "WANDER entry — capture a fragment"
echo "================================="
echo ""
echo "Type your entry (multi-line ok, empty line to finish):"

content=""
while IFS= read -r line; do
    [[ -z "$line" ]] && break
    if [[ -z "$content" ]]; then
        content="$line"
    else
        content="${content}
${line}"
    fi
done

if [[ -z "$content" ]]; then
    echo "Nothing to log."
    exit 0
fi

echo ""
read -rp "Tags (comma-separated, or Enter to skip): " tags

# add to changelog section if it exists
append_entry "$content" "$tags"

echo ""
echo "Fragment captured. It will migrate when ready."
