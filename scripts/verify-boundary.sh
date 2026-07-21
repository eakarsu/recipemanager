#!/bin/sh
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
grep -q 'retain-internal-quarantine' "$project_dir/BOUNDARY.json"
grep -q 'deployable.*false' "$project_dir/BOUNDARY.json"
grep -q 'networkExecutionAllowed.*false' "$project_dir/BOUNDARY.json"
grep -q 'ENV.fetch("SECRET_KEY_BASE")' "$project_dir/config/secrets.yml"
if grep -Eq 'secret_key_base: [a-f0-9]{40,}' "$project_dir/config/secrets.yml"; then
  echo 'Embedded cookie secret detected' >&2
  exit 1
fi
printf '%s\n' 'Archive boundary verified; no Rails server was started.'
