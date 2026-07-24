# Recipemanager — quarantined archive

This repository is a 2015 Rails 4.2.1 / Ruby 2.2.1 learning application. Those
runtime versions and the locked dependency set are obsolete and unsupported; do not
run it as a network service or use it with real identities/data. The historical app
contains recipe/chef CRUD and session login, but those legacy routes remain disabled.
Only the separate local acceptance layer described below is runnable. See
`BOUNDARY.json`, `SECURITY.md`, and `_COMPLETENESS_REVIEW.md`.

The historical Rails process remains disabled. For isolated acceptance only,
`runtime/` provides a Python 3 standard-library loopback service with PostgreSQL
identity/session storage and a narrowly authenticated AI receipt workflow. Prepare
the ignored `.env`, run `python3 runtime/migrate.py` and
`python3 runtime/create_admin.py`, then use `./start.sh`; it binds its API and UI to
the two explicit ports and never loads Rails. A production revival still requires a
separately reviewed migration to a supported Rails stack with dependency,
authorization, upload, and browser-test work.
