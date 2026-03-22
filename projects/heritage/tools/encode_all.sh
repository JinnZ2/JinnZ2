#!/usr/bin/env bash
set -euo pipefail
out="b64"
src="plaintext"
mkdir -p "$out"
for f in "$src"/*; do
  base="$(basename "$f")"
  base64 -w 0 "$f" > "$out/$base.b64"
done
echo "Encoded to $out/*.b64"
