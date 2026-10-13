import os
import math
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
APP_PIN = os.getenv("APP_PIN_CODE", "2026")

# Canterbury, Kent (CT2 7LN) Coordinates
CANTERBURY_LAT = 51.2974
CANTERBURY_LON = 1.0664


def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


@app.get("/")
def root():
    return {
        "status": "Ava LTA Personalized Radar Operational",
        "player": "Ava Pollard",
    }


@app.post("/api/verify-pin")
def verify_pin(data: dict):
    user_pin = str(data.get("pin", "")).strip()
    if user_pin == APP_PIN:
        return {"success": True, "token": SECRET_KEY}
    else:
        raise HTTPException(status_code=401, detail="Invalid PIN")


@app.get("/api/live-tournaments")
def get_tournaments(x_app_token: Optional[str] = Header(None)):
    if x_app_token != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized access token")

    # Ava's Profile Data
    ava_profile = {
        "name": "Ava Pollard",
        "ageGroup": "10U Girls",
        "recentFormPoints": 275,
        "nationalRank": 214,
    }

    # Expanded Winter Circuit through December 2026
    tournaments = [
        # --- OCTOBER 2026 ---
        {
            "id": "KEN-26-0082",
            "name": "Bromley Lawn Tennis Autumn Junior Tournament",
            "grade": "G4",
            "location": "Bromley Lawn Tennis Club, Kent",
            "distanceMiles": 48.2,
            "startDate": "24–26 Oct 2026",
            "ltaUrl": "https://competitions.lta.org.uk/find",
            "entrantsCount": 10,
            "chanceRating": "High (Top 4 Seed Potential)",
            "analysis": "With 275 points, Ava sits comfortably in the upper tier of this G4 field. Only 2 entered players have higher LTA Recent Form points.",
            "fieldEntrants": [
                {"name": "S. Taylor", "points": 340},
                {"name": "M. Davies", "points": 310},
                {"name": "Ava Pollard", "points": 275, "isUser": True},
                {"name": "E. Wilson", "points": 250},
                {"name": "L. Chen", "points": 220},
            ],
        },
        {
            "id": "KEN-26-0041",
            "name": "The Parklangley Club Autumn Grade 4",
            "grade": "G4",
            "location": "The Parklangley Club, Beckenham, Kent",
            "distanceMiles": 51.0,
            "startDate": "28–29 Oct 2026",
            "ltaUrl": "https://competitions.lta.org.uk/find",
            "entrantsCount": 12,
            "chanceRating": "Medium-High (Favorable Quarter)",
            "analysis": "Balanced G4 draw. Ava's 275 points position her well to reach the quarter-finals or better with solid tactical play.",
            "fieldEntrants": [
                {"name": "A. Smith", "points": 360},
                {"name": "H. Johnson", "points": 325},
                {"name": "Ava Pollard", "points": 275, "isUser": True},
                {"name": "P. Patel", "points": 260},
            ],
        },
        # --- NOVEMBER 2026 ---
        {
            "id": "KEN-26-0105",
            "name": "Bromley Tennis Centre Winter Regional Tour (WRT)",
            "grade": "G3",
            "location": "Bromley Tennis Centre, Orpington, Kent",
            "distanceMiles": 49.5,
            "startDate": "14–15 Nov 2026",
            "ltaUrl": "https://competitions.lta.org.uk/find",
            "entrantsCount": 16,
            "chanceRating": "Moderate (Tier 1
