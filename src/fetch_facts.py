import requests
from datetime import datetime
import pytz

WIKI_BASE = "https://en.wikipedia.org/api/rest_v1/feed/onthisday/events"

def fetch_today_events(max_events=3):
    """Fetch 1–3 events for today's date from Wikipedia OnThisDay REST API."""
    # Use UTC date to keep it stable across runner timezones
    now = datetime.utcnow()
    month = now.month
    day = now.day
    url = f"{WIKI_BASE}/{month}/{day}"
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()
        events = data.get("events", [])[:10]  # take top 10 then filter
        # Build (year, text, url) tuples
        out = []
        for ev in events:
            year = ev.get("year")
            pages = ev.get("pages", [])
            # try to pick the page with the best summary
            page = pages[0] if pages else {}
            title = page.get("titles", {}).get("normalized") or page.get("titles", {}).get("display")
            extract = (page.get("extract") or ev.get("text") or "").strip()
            page_url = page.get("content_urls", {}).get("desktop", {}).get("page") or page.get("content_urls", {}).get("mobile", {}).get("page")
            if year and title and extract and page_url:
                out.append({
                    "year": year,
                    "title": title,
                    "summary": extract,
                    "source_url": page_url
                })
            if len(out) >= max_events:
                break
        return out
    except Exception as e:
        # Fallback to a static fact if API fails
        return [{
            "year": 1969,
            "title": "Apollo 11",
            "summary": "NASA's Apollo 11 mission landed the first humans on the Moon.",
            "source_url": "https://en.wikipedia.org/wiki/Apollo_11"
        }]
