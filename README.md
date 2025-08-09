# QuickShorts Autoposter

Autogenerates and uploads 2–4 **YouTube Shorts** per day with:
- Original 18–25s script (paraphrased + optionally LLM-polished)
- Captions baked into the video (no facecam required)
- Animated background + logo watermark
- Auto title/description/hashtags with **attribution links**
- Upload via **YouTube Data API** on schedule

> Default schedule (Asia/Jerusalem): 10:00, 14:00, 18:00 daily (IDT).

## One-time setup

1) **Create a Google Cloud project** and enable **YouTube Data API v3**.
2) In **APIs & Services → Credentials**, create an **OAuth Client ID** of type **Desktop** (or Web). Download the JSON.
3) Use `get_refresh_token.py` to generate a **refresh token** for the channel that will upload. Save:
   - `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`
4) Create a **GitHub repo**, upload these files, and add **GitHub Secrets** (Settings → Secrets and variables → Actions):
   - `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`
   - Optional: `OPENAI_API_KEY` (for better script generation)
   - Optional: `BRAND_NAME` (default: QuickShorts)
   - Optional: `YT_UPLOAD_PRIVACY` (default: public)
5) Push to GitHub. Actions will run on the schedule. To test now, trigger the workflow manually in **Actions → Run workflow**.

## How it works

- `src/fetch_facts.py`: pulls 1–3 timely facts from Wikipedia **OnThisDay** REST endpoint for today (by UTC), plus a fallback.
- `src/script_writer.py`: paraphrases facts (optionally polishes with OpenAI if `OPENAI_API_KEY` is set).
- `src/render.py`: builds a 9:16 MP4 (1080x1920) with animated gradient background and large subtitles.
- `src/uploader.py`: uploads to your channel using OAuth refresh token (no manual step after first token).
- `src/main.py`: orchestrates the daily run (creates 1–3 shorts).

### Attribution & Licensing
- Description includes source URLs and a credit block (Wikipedia CC BY-SA when used).

### Notes
- **Service accounts don't work** with YouTube uploads; use OAuth with a refresh token.
- MoviePy requires **ffmpeg**; the GitHub Action installs it automatically.
- If OpenAI is off, the scripts still publish using a rules-based rephrasing to avoid copy/paste.
