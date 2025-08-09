import os
import requests

DL_PATH = "/tmp/broll.mp4"

def _search(api_key: str, query: str, per_page: int = 20):
    url = "https://api.pexels.com/videos/search"
    params = {"query": query, "per_page": per_page}
    headers = {"Authorization": api_key}
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json().get("videos", []) or []

def _pick_video(videos):
    # prefer vertical, otherwise biggest
    def is_vertical(v):
        w, h = v.get("width", 0), v.get("height", 0)
        return h > w
    vertical = [v for v in videos if is_vertical(v)]
    pool = vertical if vertical else videos
    if not pool:
        return None
    # pick largest resolution
    pool.sort(key=lambda v: v.get("width", 0) * v.get("height", 0), reverse=True)
    v = pool[0]
    files = v.get("video_files", []) or []
    if not files:
        return None
    files.sort(key=lambda f: (f.get("width", 0) * f.get("height", 0)), reverse=True)
    return files[0].get("link")

def fetch_broll(topic: str, outfile: str = DL_PATH):
    """
    Tries multiple football-related queries on Pexels.
    Returns path or None, and prints debug lines prefixed [BROLL].
    """
    api = os.getenv("PEXELS_API_KEY")
    if not api:
        print("[BROLL] No PEXELS_API_KEY set -> fallback to gradient")
        return None

    base = (topic or "football").split(";")[0].strip() or "football"
    queries = [
        f"{base} football",
        f"{base} soccer",
        "football match stadium",
        "soccer training dribble",
        "football fans stadium",
        "soccer goal celebration",
    ]

    for q in queries:
        try:
            print(f"[BROLL] Searching: {q!r}")
            vids = _search(api, q, per_page=25)
            if not vids:
                print("[BROLL]   no results")
                continue
            link = _pick_video(vids)
            if not link:
                print("[BROLL]   no usable file links")
                continue
            print(f"[BROLL] Downloading: {link}")
            data = requests.get(link, timeout=60).content
            with open(outfile, "wb") as f:
                f.write(data)
            size = os.path.getsize(outfile)
            print(f"[BROLL] Saved to {outfile} ({size/1_000_000:.1f} MB)")
            return outfile
        except Exception as e:
            print(f"[BROLL] Error while fetching: {e}")

    print("[BROLL] Could not get b-roll -> gradient fallback")
    return None
