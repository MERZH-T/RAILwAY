from flask import Flask, request
import json, base64, os

app = Flask(__name__)

ADMIN_KEY = os.getenv("ADMIN_KEY")
XOR_KEY = os.getenv("XOR_KEY")

def xor_encrypt(data: str, key: str):
    raw = data.encode()
    key = key.encode()
    out = bytearray()
    for i in range(len(raw)):
        out.append(raw[i] ^ key[i % len(key)])
    return base64.b64encode(out)

def auth_ok(req):
    return req.headers.get("Authorization") == ADMIN_KEY

@app.get("/users")
def users():
    if not auth_ok(request):
        return "Unauthorized", 401

    payload = json.dumps({"users": ["TestUser"]})
    return xor_encrypt(payload, XOR_KEY)

@app.get("/users/<username>/brainrots")
def brainrots(username):
    if not auth_ok(request):
        return "Unauthorized", 401

    payload = json.dumps([
        {
            "owner": username,
            "brainrots": [
                {"name": "Gold Rot", "gen": "$1.5m/s"}
            ]
        }
    ])
    return xor_encrypt(payload, XOR_KEY)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 3000)))
