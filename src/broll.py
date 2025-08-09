import os, requests

def fetch_broll(topic: str, outfile="broll.mp4"):
    """
    Download a portrait-ish stock clip from Pexels.
    Returns path to the saved mp4, or None if nothing found / no API key.
    """
    api = os.getenv("PEXELS_API_KEY")
    if not api:
        return None

    # make a clean, simple query for Pexels
    base = (topic.split(";")[0] or topic).strip()
    query = f"{base} soccer football"  # nudge results toward our sport

    url = "https://api.pexels.com/videos/search"
    params = {
        "query": query,
        "per_page": 20,
        "orientation": "portrait",   # Pexels may ignore this, we filter below
    }
    headers = {"Authorization": api}

    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    videos = r.json().get("videos", [])
    if not videos:
        return None

    # Prefer vertical clips; if none vertical, pick the largest anyway
    def is_vertical(v):
        w, h = v.get("width", 0), v.get("height", 0)
        return h > w

    vertical = [v for v in videos if is_vertical(v)]
    pool = vertical if vertical else videos

    # Choose biggest resolution
    def area(v): return (v.get("width", 0) * v.get("height", 0))
    pool.sort(key=area, reverse=True)
    choice = pool[0]

    files = choice.get("video_files", [])
    if not files:
        return None

    files.sort(key=lambda f: (f.get("width", 0) * f.get("height", 0)), reverse=True)
    src = files[0]["link"]

    data = requests.get(src, timeout=60).content
    with open(outfile, "wb") as f:
        f.write(data)
    return outfile
