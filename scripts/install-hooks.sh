#!/bin/sh
set -eu
cd "$(git rev-parse --show-toplevel)"
current=$(git config --get core.hooksPath || true)
if [ -n "$current" ] && [ "$current" != .githooks ]; then
  echo "Existing core.hooksPath: $current. Integrate the hooks before replacing it." >&2
  exit 1
fi
for hook in pre-commit pre-push; do
  legacy="$(git rev-parse --git-path hooks)/$hook"
  if [ -z "$current" ] && [ -f "$legacy" ]; then
    echo "Existing hook: $legacy. Integrate it before installing these hooks." >&2
    exit 1
  fi
done
chmod +x .githooks/pre-commit .githooks/pre-push
git config --local core.hooksPath .githooks
echo 'Enabled pre-commit and pre-push checks for this clone.'
