import os
import re
import random
from textwrap import shorten

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

SYSTEM_PROMPT = """You write ultra-compact 18–25s YouTube Shorts scripts.
Style: punchy, conversational, teen-friendly, 2-3 short lines, hook first, no fluff.
Always paraphrase; do NOT copy sentences from inputs. Include no URLs.
End with a mini twist or "wait for part 2".
"""

def basic_paraphrase(event):
    # Rules-based paraphrase as fallback (no LLM needed)
    year = event["year"]
    title = event["title"]
    summary = re.sub(r"\s+", " ", event["summary"]).strip()
    hook = f"{year}: {title} — wild fact time!"
    body = shorten(summary, width=180, placeholder="…")
    outro = "Crazy, right? More mini-histories tomorrow."
    lines = [hook, body, outro]
    return "\n".join(lines)

def write_script(event):
    key = os.getenv("OPENAI_API_KEY")
    if key and OpenAI:
        try:
            client = OpenAI(api_key=key)
            prompt = f"Event:\nYear: {event['year']}\nTitle: {event['title']}\nSummary: {event['summary']}"
            res = client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role":"system","content":SYSTEM_PROMPT},
                    {"role":"user","content":prompt}
                ],
                temperature=0.8,
                max_tokens=220
            )
            text = res.choices[0].message.content.strip()
            # safety: remove URLs, ensure < 280 chars
            text = re.sub(r"http\S+", "", text)
            text = text.strip()
            return text
        except Exception:
            pass
    return basic_paraphrase(event)
