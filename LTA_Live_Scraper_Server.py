import os
import math
import re
import urllib.request
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


def scrape_live_lta_competitions():
    """Renders real web searches directly from competitions.lta.org.uk."""
    tournaments = []

    # Official LTA search page URL
    lta_search_url = "https://competitions.lta.org.uk/find?Q=Kent&Distance=50"

    req = urllib.request.Request(
        lta_search_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                html_content = response.read().decode("utf-8", errors="ignore")

                # Extract tournament links and IDs from live page HTML
                matches = re.findall(
                    r'title="([^"]+)".*?href="(/tournament/([a-f0-9\-]+))"',
                    html_content,
                    re.DOTALL | re.IGNORECASE,
                )

                for idx, (title, relative_link, tourney_id) in enumerate(
                    matches[:15]
                ):
                    clean_title = title.strip()
                    if len(clean_title) < 3:
                        continue

                    tournaments.append(
                        {
                            "id": f"LTA-{tourney_id[:8].upper()}",
                            "name": clean_title,
                            "grade": (
                                "G4"
                                if "Grade 4" in clean_title
                                else (
                                    "G3"
                                    if "Grade 3" in clean_title
                                    else "LTA Event"
                                )
                            ),
                            "location": "Kent / South East Region",
                            "distanceMiles": 0.0,
                            "startDate": "Check LTA Portal",
                            "ltaUrl": f"https://competitions.lta.org.uk{relative_link}",
                            "entrantsCount": "Live Draw",
                            "chanceRating": "Official LTA Sanctioned Event",
                            "analysis": f"Official LTA event pulled live from competitions.lta.org.uk.",
                            "fieldEntrants": [
                                {
                                    "name": "Ava Pollard",
                                    "points": 275,
                                    "isUser": True,
                                }
                            ],
                        }
                    )
    except Exception as e:
        print(f"LTA Fetch Error: {e}")

    tournaments.sort(key=lambda x: x["distanceMiles"])
    return tournaments


@app.get("/api/live-tournaments")
def get_tournaments(x_app_token: Optional[str] = Header(None)):
    if x_app_token != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized access token")

    ava_profile = {
        "name": "Ava Pollard",
        "ageGroup": "10U Girls",
        "recentFormPoints": 275,
        "nationalRank": 214,
    }

    live_tournaments = scrape_live_lta_competitions()

    return {"playerProfile": ava_profile, "tournaments": live_tournaments}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
