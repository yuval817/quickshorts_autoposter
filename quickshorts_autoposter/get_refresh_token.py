"""
Use this once to print a refresh token for your channel.
1) Create OAuth 2.0 Client ID (Desktop app) in Google Cloud Console.
2) Put the client_id and client_secret in env vars or paste directly.
3) Run `python get_refresh_token.py` locally, follow the browser auth, copy the code.
4) Save the printed refresh token as `YT_REFRESH_TOKEN` in GitHub Secrets.
"""
import os, webbrowser, urllib.parse, requests

CLIENT_ID = os.getenv("YT_CLIENT_ID") or input("Client ID: ").strip()
CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET") or input("Client Secret: ").strip()
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"

SCOPE = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"

auth_url = (
    "https://accounts.google.com/o/oauth2/v2/auth?"
    + urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent"
    })
)

print("Open this URL in your browser, log in to the channel account, and paste the code:")
print(auth_url)
try:
    webbrowser.open(auth_url)
except Exception:
    pass

code = input("Paste auth code: ").strip()
token_resp = requests.post("https://oauth2.googleapis.com/token", data={
    "code": code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code"
}, timeout=20)

print("Token response:", token_resp.json())
print("\nSave this refresh_token in GitHub Secrets as YT_REFRESH_TOKEN:")
print(token_resp.json().get("refresh_token"))
