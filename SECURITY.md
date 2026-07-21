# Security status

This repository is quarantined. Do not start the Rails server, expose it to a network,
or use real accounts/uploads/data. Ruby 2.2.1, Rails 4.2.1, and the 2015 lockfile are
outside supported security lifecycles.

Previously checked-in development/test cookie-signing values were removed from the
current tree and must not be reused. Their presence in Git history means they are public
and permanently invalid for any future deployment. A revival requires a clean supported
runtime, dependency review, new secrets, authorization review, migrations, and automated
login/CRUD/upload tests.
