import os
import math
import requests
import uvicorn
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI(title="Ava LTA Tournament Radar API")

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

SECRET_KEY = os.getenv("APP_SECRET_KEY", "AGP2026!")

CANTERBURY_LAT = 51.2974
CANTERBURY_LON = 1.0664

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
R = 3958.8 # Earth radius in miles
dlat = math.radians(lat2 - lat1)
dlon = math.radians(lon2 - lon1)
a = (math.sin(dlat / 2) ** 2 +
math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
math.sin(dlon / 2) ** 2)
c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
return round(R * c, 1)

@app.get("/")
def root():
return {"status": "Live LTA Matchup API Operational", "player": "Ava Pollard"}

@app.get("/api/live-tournaments")
def get_tournaments(x_app_token: Optional[str] = Header(None)):
if x_app_token != SECRET_KEY:
raise HTTPException(status_code=403, detail="Unauthorized access token")

headers = {
"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
"Accept": "application/json, text/plain, */*",
"Referer": "https://competitions.lta.org.uk/find"
}

lta_api_url = "https://competitions.lta.org.uk/api/tournament/search"

params = {
"distance": 100,
"latitude": CANTERBURY_LAT,
"longitude": CANTERBURY_LON,
"ageGroup": "10U",
"status": "OpenForEntry"
}

tournaments = []

try:
response = requests.get(lta_api_url, headers=headers, params=params, timeout=10)
if response.status_code == 200:
raw_data = response.json()
items = raw_data.get("items", []) if isinstance(raw_data, dict) else raw_data

for item in items:
grade_val = str(item.get("grade", ""))
if "3" in grade_val or "4" in grade_val:
v_lat = item.get("latitude", CANTERBURY_LAT)
v_lon = item.get("longitude", CANTERBURY_LON)
dist = calculate_haversine_distance(CANTERBURY_LAT, CANTERBURY_LON, v_lat, v_lon)

if dist <= 100:
tournaments.append({
"id": str(item.get("id", "")),
"name": item.get("name", "10U Tournament"),
"grade": f"G{item.get('grade', 4)}",
"location": item.get("venueName", "LTA Venue"),
"distanceMiles": dist,
"startDate": item.get("startDate", "Upcoming"),
"ltaUrl": f"https://competitions.lta.org.uk/tournament/{item.get('code', '')}",
"entrantsCount": item.get("entrantsCount", 0)
})
except Exception as e:
print(f"API Error: {e}")

tournaments.sort(key=lambda x: x["distanceMiles"])
return tournaments

if __name__ == "__main__":
port = int(os.environ.get("PORT", 10000))
uvicorn.run(app, host="0.0.0.0", port=port)
