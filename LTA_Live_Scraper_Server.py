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

# CT2 7LN Coordinates (Canterbury, Kent)
CANTERBURY_LAT = 51.2974
CANTERBURY_LON = 1.0664

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
"""Calculate distance in miles between two coordinates."""
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

# Official LTA Tournament Search API Endpoint
lta_api_url = "https://competitions.lta.org.uk/api/tournament/search"

# Search parameters for 10U, G3 & G4 open entries
params = {
"distance": 100,
"latitude": CANTERBURY_LAT,
"longitude": CANTERBURY_LON,
"ageGroup": "10U",
"grades": "3,4",
"status": "OpenForEntry"
}

tournaments = []

try:
response = requests.get(lta_api_url, params=params, timeout=10)

if response.status_code == 200:
raw_data = response.json()
items = raw_data.get("items", []) if isinstance(raw_data, dict) else raw_data

for item in items:
# Extract coordinates if available
venue_lat = item.get("latitude", CANTERBURY_LAT)
venue_lon = item.get("longitude", CANTERBURY_LON)
dist = calculate_haversine_distance(CANTERBURY_LAT, CANTERBURY_LON, venue_lat, venue_lon)

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
print(f"LTA API Query Error: {e}")

# Return sorted by distance from Canterbury
tournaments.sort(key=lambda x: x["distanceMiles"])
return tournaments

if __name__ == "__main__":
port = int(os.environ.get("PORT", 10000))
uvicorn.run(app, host="0.0.0.0", port=port)
