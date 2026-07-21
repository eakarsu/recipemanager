# Recipemanager — quarantined archive

This repository is a 2015 Rails 4.2.1 / Ruby 2.2.1 learning application. Those
runtime versions and the locked dependency set are obsolete and unsupported; do not
run it as a network service or use it with real identities/data. The historical app
contains recipe/chef CRUD and session login, but no current runtime or login success is
claimed. See `BOUNDARY.json`, `SECURITY.md`, and `_COMPLETENESS_REVIEW.md`.

`./start.sh` performs an offline archive-boundary check only. A future revival must be
a separately reviewed migration to a supported Ruby/Rails stack with dependency,
database, authentication, authorization, upload, and browser-test work.
