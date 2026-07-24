#!/usr/bin/env python3
"""Supported local acceptance runtime; the quarantined Rails application is never loaded."""

import base64
import hashlib
import hmac
import json
import os
import secrets
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def required(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def sql_text(value):
    encoded = base64.b64encode(value.encode("utf-8")).decode("ascii")
    return f"convert_from(decode('{encoded}','base64'),'UTF8')"


def query(sql):
    result = subprocess.run(
        ["psql", "--no-psqlrc", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1", required("DATABASE_URL"), "-c", sql],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        raise RuntimeError("database operation failed")
    return [line for line in result.stdout.splitlines() if line]


def password_digest(password, salt):
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)


def json_bytes(value):
    return json.dumps(value, separators=(",", ":")).encode("utf-8")


class ApiHandler(BaseHTTPRequestHandler):
    server_version = "RecipeRuntime/1"

    def log_message(self, format_string, *args):
        sys.stdout.write("api " + format_string % args + "\n")
        sys.stdout.flush()

    def cors_headers(self):
        origin = self.headers.get("Origin")
        allowed = f"http://127.0.0.1:{required('FRONTEND_PORT')}"
        if origin == allowed:
            self.send_header("Access-Control-Allow-Origin", allowed)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def respond(self, status, value):
        body = json_bytes(value)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length < 1 or length > 65536:
            raise ValueError("request body must contain 1 to 65536 bytes")
        return json.loads(self.rfile.read(length))

    def identity(self):
        authorization = self.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return None
        token = authorization[7:]
        if len(token) != 64 or any(char not in "0123456789abcdef" for char in token):
            return None
        token_hash = hashlib.sha256(token.encode("ascii")).hexdigest()
        rows = query(
            "SELECT u.id,u.email,u.display_name FROM runtime_sessions s "
            "JOIN runtime_users u ON u.id=s.user_id "
            f"WHERE s.token_hash='{token_hash}' AND s.expires_at>NOW() AND u.active=TRUE"
        )
        if not rows:
            return None
        user_id, email, display_name = rows[0].split("|", 2)
        return {"id": int(user_id), "email": email, "name": display_name}

    def do_OPTIONS(self):
        self.send_response(204)
        self.cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            query("SELECT 1 FROM runtime_schema_migrations LIMIT 1")
            return self.respond(200, {"status": "ok"})
        if self.path == "/api/auth/me":
            user = self.identity()
            return self.respond(200, {"user": user}) if user else self.respond(401, {"error": "Authentication required"})
        return self.respond(404, {"error": "Not found"})

    def do_POST(self):
        try:
            if self.path == "/api/auth/login":
                return self.login()
            if self.path == "/api/ai/recommendation":
                return self.ai_recommendation()
            return self.respond(404, {"error": "Not found"})
        except (ValueError, json.JSONDecodeError):
            return self.respond(400, {"error": "Invalid request"})
        except (RuntimeError, urllib.error.URLError, TimeoutError) as error:
            self.log_error("request failure: %s", type(error).__name__)
            return self.respond(503, {"error": "Service unavailable"})

    def login(self):
        body = self.read_json()
        email = str(body.get("email", "")).strip().lower()
        password = str(body.get("password", ""))
        if not email or len(password) > 256:
            return self.respond(401, {"error": "Invalid credentials"})
        rows = query(
            "SELECT id,email,display_name,password_salt,password_hash FROM runtime_users "
            f"WHERE email={sql_text(email)} AND active=TRUE"
        )
        if not rows:
            password_digest(password, b"0" * 16)
            return self.respond(401, {"error": "Invalid credentials"})
        user_id, stored_email, display_name, salt_hex, hash_hex = rows[0].split("|", 4)
        actual = password_digest(password, bytes.fromhex(salt_hex)).hex()
        if not hmac.compare_digest(actual, hash_hex):
            return self.respond(401, {"error": "Invalid credentials"})
        token = secrets.token_hex(32)
        token_hash = hashlib.sha256(token.encode("ascii")).hexdigest()
        expires = (datetime.now(timezone.utc) + timedelta(hours=8)).isoformat()
        query(
            "INSERT INTO runtime_sessions(token_hash,user_id,expires_at) "
            f"VALUES('{token_hash}',{int(user_id)},{sql_text(expires)}::timestamptz)"
        )
        return self.respond(200, {"token": token, "user": {"id": int(user_id), "email": stored_email, "name": display_name}})

    def ai_recommendation(self):
        user = self.identity()
        if not user:
            return self.respond(401, {"error": "Authentication required"})
        body = self.read_json()
        prompt = str(body.get("prompt", "")).strip()
        if not prompt or len(prompt) > 4000:
            return self.respond(400, {"error": "prompt must contain 1 to 4000 characters"})
        model = required("OPENROUTER_MODEL")
        upstream_body = json_bytes({
            "model": model,
            "messages": [
                {"role": "system", "content": "Give one concise, practical recipe organization recommendation."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 160,
        })
        request = urllib.request.Request(
            required("OPENROUTER_BASE_URL").rstrip("/") + "/chat/completions",
            data=upstream_body,
            method="POST",
            headers={
                "Authorization": "Bearer " + required("OPENROUTER_API_KEY"),
                "Content-Type": "application/json",
                "HTTP-Referer": f"http://127.0.0.1:{required('FRONTEND_PORT')}",
                "X-Title": "Recipe Manager Runtime Verification",
            },
        )
        with urllib.request.urlopen(request, timeout=45) as response:
            payload = json.loads(response.read())
        content = str(payload.get("choices", [{}])[0].get("message", {}).get("content", "")).strip()
        provider_id = str(payload.get("id", "")).strip()
        resolved_model = str(payload.get("model") or model).strip()
        if not content or not provider_id:
            raise RuntimeError("incomplete provider response")
        rows = query(
            "INSERT INTO runtime_ai_receipts(user_id,prompt,content,provider,provider_request_id,model) VALUES("
            f"{user['id']},{sql_text(prompt)},{sql_text(content)},'openrouter',{sql_text(provider_id)},{sql_text(resolved_model)}) RETURNING id"
        )
        return self.respond(200, {
            "content": content,
            "receipt": {"id": int(rows[0]), "provider": "openrouter", "provider_request_id": provider_id, "model": resolved_model},
        })


class UiHandler(BaseHTTPRequestHandler):
    def log_message(self, format_string, *args):
        sys.stdout.write("ui " + format_string % args + "\n")
        sys.stdout.flush()

    def do_GET(self):
        if self.path not in ("/", "/login"):
            self.send_error(404)
            return
        api_url = f"http://127.0.0.1:{required('BACKEND_PORT')}"
        body = f"""<!doctype html><html><head><meta charset='utf-8'><title>Recipe Manager Login</title></head>
<body><main><h1>Recipe Manager</h1><p>Supported local acceptance runtime; the legacy Rails archive remains disabled.</p>
<form id='login'><input id='email' type='email' placeholder='Email' required><input id='password' type='password' placeholder='Password' required><button>Sign in</button></form><pre id='result'></pre></main>
<script>document.getElementById('login').onsubmit=async(e)=>{{e.preventDefault();const r=await fetch('{api_url}/api/auth/login',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:email.value,password:password.value}})}});result.textContent=r.ok?'Signed in': 'Login failed';}};</script></body></html>""".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'; connect-src http://127.0.0.1:*")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)


def serve(mode):
    if mode == "api":
        query("SELECT 1 FROM runtime_schema_migrations LIMIT 1")
        port, handler = int(required("BACKEND_PORT")), ApiHandler
    elif mode == "ui":
        port, handler = int(required("FRONTEND_PORT")), UiHandler
    else:
        raise RuntimeError("mode must be api or ui")
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"Recipe runtime {mode} listening on http://127.0.0.1:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    serve(sys.argv[1] if len(sys.argv) > 1 else "")
