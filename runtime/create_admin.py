#!/usr/bin/env python3
import os
import secrets
from runtime_server import password_digest, query, sql_text

email = (os.environ.get("ADMIN_EMAIL") or os.environ.get("PROVISION_ADMIN_EMAIL") or "").strip().lower()
password = os.environ.get("ADMIN_PASSWORD") or os.environ.get("PROVISION_ADMIN_PASSWORD") or ""
name = (os.environ.get("PROVISION_ADMIN_NAME") or "Runtime Administrator").strip()
if "@" not in email or len(password) < 12 or len(password) > 128 or not name:
    raise RuntimeError("valid administrator email, name, and a 12-128 character password are required")
salt = secrets.token_bytes(16)
digest = password_digest(password, salt)
query(
    "INSERT INTO runtime_users(email,display_name,password_salt,password_hash) VALUES("
    f"{sql_text(email)},{sql_text(name)},'{salt.hex()}','{digest.hex()}') "
    "ON CONFLICT(email) DO UPDATE SET display_name=EXCLUDED.display_name,password_salt=EXCLUDED.password_salt,password_hash=EXCLUDED.password_hash,active=TRUE"
)
print("Recipe runtime administrator is ready")
