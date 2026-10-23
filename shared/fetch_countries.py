import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()  # reads RESTCOUNTRIES_API_KEY from the .env file
API_KEY = os.getenv("RESTCOUNTRIES_API_KEY")
if not API_KEY:
    raise SystemExit("Missing RESTCOUNTRIES_API_KEY. Add it to your .env file.")

URL = "https://api.restcountries.com/countries/v5"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
FIELDS = "names.common,codes.alpha_2,region,population,capitals,flag.url_png"

countries = []
offset = 0
while True:
    response = requests.get(
        URL,
        headers=HEADERS,
        params={"response_fields": FIELDS, "limit": 100, "offset": offset},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()["data"]

    # Flatten into the simple shape both of our APIs will use
    for c in data["objects"]:
        if not c["codes"].get("alpha_2"):
            continue  # skip territories without an ISO code (e.g. Somaliland)
        capitals = c.get("capitals") or []
        countries.append({
            "code": c["codes"]["alpha_2"],
            "name": c["names"]["common"],
            "region": c["region"],
            "population": c["population"],
            "capital": capitals[0]["name"] if capitals else None,
            "flag": c["flag"]["url_png"],
        })

    more = data["meta"].get("more")
    if more is None:  # fall back: a full page means there may be another
        more = len(data["objects"]) == 100
    if not more:
        break
    offset += 100

countries.sort(key=lambda x: x["name"])

with open("shared/countries.json", "w", encoding="utf-8") as f:
    json.dump(countries, f, ensure_ascii=False, indent=2)

print(f"Saved {len(countries)} countries to shared/countries.json")