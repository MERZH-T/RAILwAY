import time
import base64
import json
import requests
import re
from datetime import datetime

# ================================
# CONFIGURATION
# ================================
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1475316636394455040/-Dl5k96Ker-3QFlDrdc0JPgY7m1FXXL1rCj_Ily1hPvCZYrIOzjZtDUWJkkDQM7b4Aeg"
API_BASE = "https://railway-production-b7aa.up.railway.app"
ADMIN_KEY = "i-need-to-make-this-long-otherwise-its-not-secure-popcorn12"
XOR_KEY = "purple-dragon-72"
POLL_INTERVAL = 3  # Check every 3 seconds

# ================================
# SECURITY & PARSING 
# ================================
def xor_decrypt(encoded: str, key: str) -> str:
    try:
        decoded = base64.b64decode(encoded)
        result = bytearray()
        key_bytes = key.encode('utf-8')
        for i in range(len(decoded)):
            result.append(decoded[i] ^ key_bytes[i % len(key_bytes)])
        return result.decode('utf-8')
    except Exception as e:
        return ""

def parse_gen(gen_str):
    """Parses '$1.5k/s' into a raw number for sorting, exactly like the Lua tracker"""
    if not gen_str: return 0
    match = re.search(r'[\d\.]+', gen_str)
    if not match: return 0
    num = float(match.group())
    lower_s = gen_str.lower()
    if 'k' in lower_s: num *= 1_000
    elif 'm' in lower_s: num *= 1_000_000
    elif 'b' in lower_s: num *= 1_000_000_000
    return num

# ================================
# API INTERACTIONS
# ================================
def get_active_users():
    url = f"{API_BASE}/users"
    headers = {"Authorization": ADMIN_KEY}
    try:
        req = requests.get(url, headers=headers, timeout=10)
        if req.status_code == 200:
            decrypted = xor_decrypt(req.text, XOR_KEY)
            return json.loads(decrypted).get("users", [])
    except Exception:
        pass
    return []

def get_user_brainrots(username):
    url = f"{API_BASE}/users/{username}/brainrots"
    headers = {"Authorization": ADMIN_KEY}
    try:
        req = requests.get(url, headers=headers, timeout=10)
        if req.status_code == 200:
            decrypted = xor_decrypt(req.text, XOR_KEY)
            return json.loads(decrypted)
    except Exception:
        pass
    return None

# ================================
# BEAUTIFUL DISCORD EMBED BUILDER
# ================================
def send_discord_webhook(username, target_brs, server_brs):
    # Sort from highest generation output to lowest
    target_brs.sort(key=lambda x: x["gen_val"], reverse=True)
    server_brs.sort(key=lambda x: x["gen_val"], reverse=True)
    
    # Determine the color theme exactly like the tabs in the UI Script
    highest_gen = target_brs[0]["gen_val"] if target_brs else 0
    if highest_gen >= 50_000_000:
        color = 5301368  # 🟢 Clean Hits (Green / #50DC78)
    elif highest_gen >= 10_000_000:
        color = 16757810 # 🟠 Mid Hits (Orange / #FFB432)
    elif highest_gen >= 1_000_000:
        color = 16732240 # 🔴 Trash Hits (Red / #FF5050)
    else:
        color = 5301368  # Default Green
        
    embed = {
        "title": f"⚡ Hits Tracker Monitor - {username}",
        "description": f"Found new brainrot updates for **{username}**!",
        "color": color,
        "fields": [],
        "thumbnail": {
            "url": "https://tr.rbxcdn.com/38c6edcb50633730ff4cf39ac8859840/420/420/Hat/Png"
        },
        "footer": {
            "text": "Live API Tracker Engine • Auto Updated",
            "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Twitter_Verified_Badge.svg/512px-Twitter_Verified_Badge.svg.png"
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    # Helper function: Discord crashes if fields have >1024 characters.
    # This automatically splits massive server lists into beautiful chunks.
    def chunk_list(br_list, is_server=False):
        lines = []
        for br in br_list:
            if is_server:
                lines.append(f"👤 **{br['owner']}**: {br['name']} - 💸 **{br['gen']}**")
            else:
                lines.append(f"⭐ {br['name']} - 💸 **{br['gen']}**")
                
        chunks, current = [], ""
        for line in lines:
            if len(current) + len(line) > 1000:
                chunks.append(current)
                current = line + "\n"
            else:
                current += line + "\n"
        if current:
            chunks.append(current)
        return chunks

    # --- 1) SERVER BRAINROTS ---
    if server_brs:
        for i, chunk in enumerate(chunk_list(server_brs, is_server=True)):
            title = "🏆 Brainrots in server" if i == 0 else "🏆 Brainrots in server (Cont.)"
            embed["fields"].append({"name": title, "value": chunk, "inline": False})
    else:
        embed["fields"].append({"name": "🏆 Brainrots in server", "value": "None found", "inline": False})
        
    # --- 2) TARGET BRAINROTS ---
    if target_brs:
        for i, chunk in enumerate(chunk_list(target_brs, is_server=False)):
            title = f"✨ Brainrots from {username}" if i == 0 else f"✨ Brainrots from {username} (Cont.)"
            embed["fields"].append({"name": title, "value": chunk, "inline": False})

    payload = {
        "username": "Hits Tracker Engine",
        "embeds": [embed]
    }
    
    try:
        res = requests.post(DISCORD_WEBHOOK, json=payload)
        if res.status_code in (200, 204):
            print(f"[+] Successfully pushed beautiful Embed to Discord for {username}!")
    except Exception as e:
        print(f"[-] Discord Webhook threw an error: {e}")

# ================================
# MAIN LOOP ENGINE
# ================================
def main():
    print("🚀 Auto-Tracker Engine Started. Listening for API changes...")
    
    # Keeps track of what plots we've already seen so we don't spam duplicate hooks
    known_user_states = {} 
    
    while True:
        try:
            active_users = get_active_users()
            
            # 1. Clean up users who left the game/API list
            for u in list(known_user_states.keys()):
                if u not in active_users:
                    print(f"👋 {u} left the session.")
                    del known_user_states[u]

            # 2. Poll every active user's setup
            for user in active_users:
                plots = get_user_brainrots(user)
                if plots is None:
                    continue 
                
                target_brs = []
                server_brs = []
                
                for plot in plots:
                    owner = plot.get("owner")
                    if owner and owner != "Empty":
                        for br in plot.get("brainrots", []):
                            br_data = {
                                "name": br.get("name", "Unknown"),
                                "gen": br.get("gen", "0/s"),
                                "gen_val": parse_gen(br.get("gen", "")),
                                "owner": owner
                            }
                            if owner == user:
                                target_brs.append(br_data)
                            else:
                                server_brs.append(br_data)
                                
                # Create a string representation to detect if the data legitimately changed
                current_state = json.dumps(target_brs, sort_keys=True)
                prev_state = known_user_states.get(user)
                
                # If we've never seen this user before OR their brainrots updated...
                if current_state != prev_state:
                    known_user_states[user] = current_state
                    
                    if len(target_brs) > 0:
                        print(f"⚠️ Brainrots loaded for {user}! Packaging UI webhook...")
                        send_discord_webhook(user, target_brs, server_brs)
                    else:
                        print(f"ℹ️ {user} is loaded but has 0 items (Ignoring for now).")
                        
        except Exception as e:
            print(f"[-] Polling Loop caught an exception: {e}")
            
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
