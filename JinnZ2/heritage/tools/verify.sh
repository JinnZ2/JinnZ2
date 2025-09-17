#!/usr/bin/env bash
set -euo pipefail
mkdir -p .verify_tmp
ok=1
for f in b64/*.b64; do
  raw=".verify_tmp/$(basename "${f%.b64}")"
  base64 -d "$f" > "$raw"
  if ! diff -q "$raw" "plaintext/$(basename "$raw")" >/dev/null; then
    echo "Mismatch: $f"
    ok=0
  fi
done
rm -rf .verify_tmp
[ $ok -eq 1 ] && echo "All good." || (echo "Some files differ." && exit 1)
