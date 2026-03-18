"""
run_ngrok.py — Starts ngrok tunnel and prints the WhatsApp webhook URL.

USAGE:
    python run_ngrok.py

This will:
1. Create a public HTTPS tunnel to your local port 8000
2. Print the webhook URL you need to paste into Meta Developer Console
3. Keep running so the tunnel stays alive

You need a free ngrok account: https://dashboard.ngrok.com/signup
Then set your authtoken once:
    ngrok config add-authtoken YOUR_TOKEN
"""

from pyngrok import ngrok, conf
import time
import os

VERIFY_TOKEN = "kisan_saathi_secure_token_2024"
NGROK_AUTH_TOKEN = "37YtdmtkOVMc3DCuck4AbYClZXT_7MVDGGzqQBGLf4EuFWBtx"

# Set authtoken via pyngrok (no need for ngrok to be installed system-wide)
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

print("🌾 Kisan Saathi — Starting ngrok tunnel...")
print("━" * 50)

# Start tunnel on port 8000 (where uvicorn runs)
tunnel = ngrok.connect(8000, "http")
public_url = tunnel.public_url

# Force HTTPS
if public_url.startswith("http://"):
    public_url = "https://" + public_url[7:]

webhook_url = f"{public_url}/webhook"

print(f"\n✅ Tunnel active!")
print(f"\n📱 WHATSAPP WEBHOOK SETUP:")
print(f"━" * 50)
print(f"1. Go to: https://developers.facebook.com/apps/")
print(f"2. Select your app → WhatsApp → Configuration")
print(f"3. Click 'Edit' on Webhook")
print(f"4. Callback URL  →  {webhook_url}")
print(f"5. Verify Token  →  {VERIFY_TOKEN}")
print(f"6. Click 'Verify and Save'")
print(f"7. Subscribe to 'messages' field")
print(f"━" * 50)
print(f"\n🌐 Public URL: {public_url}")
print(f"📡 Webhook  : {webhook_url}")
print(f"\n⚠️  Keep this script running! Ctrl+C to stop.\n")

try:
    while True:
        time.sleep(30)
        # Re-print URL every 30s so you don't lose it
        print(f"[Still running] Webhook: {webhook_url}")
except KeyboardInterrupt:
    print("\n🛑 Stopping ngrok tunnel...")
    ngrok.disconnect(public_url)
    ngrok.kill()
    print("Done.")
