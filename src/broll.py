import os, requests

def fetch_broll(topic: str, outfile="broll.mp4"):
    """
    Download a portrait-ish stock clip from Pexels matching `topic`.
    Returns path to the saved mp4, or None if nothing found / no API key.
    """
    api = os.getenv("PEXELS_API_KEY")
    if not api:
        return None

    url = "https://api.pexels.com/videos/search"
    params = {"query": topic, "per_page": 15}
    headers = {"Authorization": api}

    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    videos = r.json().get("videos", [])
    if not videos:
        return None

    # Prefer tall clips (portrait). Fall back to best available.
    videos.sort(key=lambda v: (v.get("height", 1) / max(1, v.get("width", 1))), reverse=True)
    choice = videos[0]
    files = choice.get("video_files", [])
    if not files:
        return None

    files.sort(key=lambda f: (f.get("width", 0) * f.get("height", 0)), reverse=True)
    src = files[0]["link"]

    data = requests.get(src, timeout=60).content
    with open(outfile, "wb") as f:
        f.write(data)
    return outfile
