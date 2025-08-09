import os
from moviepy.editor import (
    ImageClip, CompositeVideoClip, ColorClip, concatenate_videoclips,
    VideoFileClip, vfx
)
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap

W, H = 1080, 1920
DURATION = 22  # seconds

def gradient_bg(duration=DURATION):
    colors = [(20,20,30), (35,20,60), (20,40,80), (15,15,35)]
    clips = [ColorClip(size=(W,H), color=c, duration=max(1, duration//len(colors) or 1)) for c in colors]
    return concatenate_videoclips(clips, method="compose")

def make_text_image(script: str, brand: str):
    lines = []
    for raw in script.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        lines.append(textwrap.fill(raw, width=22))
    caption = "\n\n".join(lines)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        wm_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
    except Exception:
        font = ImageFont.load_default(); wm_font = ImageFont.load_default()

    img = Image.new("RGBA", (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    bbox = draw.multiline_textbbox((0,0), caption, font=font, spacing=8, align="center")
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x = (W - tw)//2
    y = (H - th)//2 - 40
    draw.multiline_text((x,y), caption, font=font, fill=(255,255,255,230), align="center", spacing=8)

    wm_bbox = draw.textbbox((0,0), brand, font=wm_font)
    wmw = wm_bbox[2]-wm_bbox[0]
    wmx = (W - wmw)//2
    wmy = H - 120
    draw.text((wmx, wmy), brand, font=wm_font, fill=(255,255,255,220))
    return np.array(img)

def make_background(topic: str | None):
    """
    Try to fetch football b-roll via Pexels; fall back to an animated gradient.
    """
    try:
        from broll import fetch_broll
        if topic:
            path = fetch_broll(topic, outfile="broll.mp4")
            if path and os.path.exists(path):
                clip = VideoFileClip(path).without_audio()

                # Fit to 9:16 (1080x1920) with a smart center crop
                scale = H / clip.h
                resized = clip.resize(scale)
                if resized.w >= W:
                    x1 = int((resized.w - W) / 2)
                    bg = resized.crop(x1=x1, y1=0, x2=x1 + W, y2=H)
                else:
                    bg = resized.resize(width=W).crop(y1=0, y2=H)

                # Trim to duration + slight color boost for punch
                bg = bg.subclip(0, min(DURATION, bg.duration)).fx(vfx.colorx, 1.06)
                return bg
    except Exception:
        pass

    return gradient_bg()

def render_video(script: str, brand_name: str = "QuickShorts",
                 outfile: str = "out.mp4", topic: str | None = None):
    bg = make_background(topic)
    overlay_np = make_text_image(script, brand_name)
    overlay = ImageClip(overlay_np).set_duration(bg.duration).set_opacity(0.98)
    final = CompositeVideoClip([bg, overlay], size=(W,H))
    final.write_videofile(outfile, fps=30, codec="libx264", audio=False,
                          preset="medium", threads=2)
    return outfile
