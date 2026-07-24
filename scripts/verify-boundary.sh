#!/bin/sh
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
grep -q 'retain-internal-quarantine' "$project_dir/BOUNDARY.json"
grep -q 'deployable.*false' "$project_dir/BOUNDARY.json"
grep -q 'networkExecutionAllowed.*supported-local-runtime-only' "$project_dir/BOUNDARY.json"
grep -q 'ENV.fetch("SECRET_KEY_BASE")' "$project_dir/config/secrets.yml"
if grep -Eq 'secret_key_base: [a-f0-9]{40,}' "$project_dir/config/secrets.yml"; then
  echo 'Embedded cookie secret detected' >&2
  exit 1
fi
python3 -m py_compile "$project_dir"/runtime/*.py
grep -q 'Ruby 2.2.1 / Rails 4.2.1 remains disabled' "$project_dir/BOUNDARY.json"
printf '%s\n' 'Archive boundary and supported loopback acceptance layer verified; Rails was not started.'
