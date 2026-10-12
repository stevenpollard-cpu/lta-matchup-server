import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import math
import os

# -------------------------------------------------------------------
# SECURITY CONFIGURATION
# Set your secret token. Only requests sending this header will be accepted.
# -------------------------------------------------------------------
SECRET_API_KEY = os.environ.get("APP_SECRET_KEY", "AvaPollard2026SecretKey!")

app = FastAPI(title="Live LTA 10U Matchup API")

# Enable CORS for cross-origin browser access from mobile devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Reference Coordinates for Postcode CT2 7LN (Canterbury)
ORIGIN_LAT = 51.297
ORIGIN_LON = 1.071

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates distance in miles between two coordinates."""
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

@app.get("/")
def home():
    return {"status": "Live LTA Matchup API Operational", "player": "Ava Pollard"}

@app.get("/api/live-tournaments")
def get_live_tournaments(
    postcode: str = Query("CT27LN"),
    radius: float = Query(100.0),
    x_app_token: str = Header(None)
):
    """
    Scrapes live 10U Grade 3 & Grade 4 tournament records from LTA Competitions.
    Requires secret x_app_token header for authorization.
    """
    # 1. Security Check
    if x_app_token != SECRET_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid Secret Access Token")

    # 2. Target LTA Competition Search API URL
    lta_search_url = "https://competitions.lta.org.uk/find"
    params = {
        "AgeGroup": "10U",
        "Grade": "3,4",
        "Distance": radius,
        "Postcode": postcode
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
    }

    tournaments_list = []

    try:
        response = requests.get(lta_search_url, params=params, headers=headers, timeout=10)
        
        # Parse HTML response if available
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all('div', class_='tournament-card')
            
            for card in cards:
                title_elem = card.find('h3') or card.find('a', class_='title')
                code_elem = card.find('span', class_='code')
                venue_elem = card.find('span', class_='venue')
                date_elem = card.find('span', class_='date')
                link_elem = card.find('a', href=True)
                
                if title_elem:
                    name = title_elem.text.strip()
                    code = code_elem.text.strip() if code_elem else "10U G4"
                    venue = venue_elem.text.strip() if venue_elem else "Kent / South East Venue"
                    dates = date_elem.text.strip() if date_elem else "Upcoming 2026"
                    link = link_elem['href'] if link_elem else "https://competitions.lta.org.uk"
                    
                    if not link.startswith("http"):
                        link = f"https://competitions.lta.org.uk{link}"
                        
                    tournaments_list.append({
                        "id": code,
                        "code": code,
                        "name": name,
                        "venue": venue,
                        "dates": dates,
                        "distance": 15.5,
                        "grade": 3 if "G3" in code or "Grade 3" in name else 4,
                        "link": link,
                        "entrants": []
                    })
    except Exception as e:
        print(f"Scraping note: {str(e)}")

    return {
        "postcode": postcode,
        "radius": radius,
        "total_events": len(tournaments_list),
        "tournaments": tournaments_list
    }

if __name__ == "__main__":
    uvicorn.run("lta_scraper_server:app", host="0.0.0.0", port=8000, reload=True)