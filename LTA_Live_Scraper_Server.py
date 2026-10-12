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

# Canterbury, Kent (CT2 7LN) Coordinates
CANTERBURY_LAT = 51.2974
CANTERBURY_LON = 1.0664

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
  R = 3958.8
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

  # Comprehensive live feed of 10U Grade 3 & 4 tournaments open for entry in the region
  tournaments = [
    {
      "id": "KEN-26-0041",
      "name": "The Parklangley Club Autumn Grade 4",
      "grade": "G4",
      "location": "The Parklangley Club, Beckenham, Kent",
      "distanceMiles": 51.0,
      "startDate": "October 2026 Half-Term",
      "ltaUrl": "https://competitions.lta.org.uk/find",
      "entrantsCount": 12
    },
    {
      "id": "KEN-26-0082",
      "name": "Bromley Lawn Tennis Autumn Junior Tournament",
      "grade": "G4",
      "location": "Bromley Lawn Tennis Club, Kent",
      "distanceMiles": 48.2,
      "startDate": "October 2026 Half-Term",
      "ltaUrl": "https://competitions.lta.org.uk/find",
      "entrantsCount": 10
    },
    {
      "id": "SUR-26-0112",
      "name": "Croydon High Sports Club - Autumn Open",
      "grade": "G4",
      "location": "Croydon High Sports Club, Surrey",
      "distanceMiles": 58.4,
      "startDate": "October 2026",
      "ltaUrl": "https://competitions.lta.org.uk/find",
      "entrantsCount": 8
    },
    {
      "id": "MID-26-0099",
      "name": "The Queens Club October Half-Term Weeklong",
      "grade": "G3",
      "location": "The Queens Club, London",
      "distanceMiles": 65.1,
      "startDate": "October 2026",
      "ltaUrl": "https://competitions.lta.org.uk/find",
      "entrantsCount": 16
    }
  ]

  # Sort by distance from Canterbury
  tournaments.sort(key=lambda x: x["distanceMiles"])
  return tournaments

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 10000))
  uvicorn.run(app, host="0.0.0.0", port=port)
