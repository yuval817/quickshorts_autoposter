import os
from moviepy.editor import (
    ImageClip, CompositeVideoClip, ColorClip, concatenate_videoclips,
    VideoFileClip, vfx, AudioFileClip
)
from moviepy.audio.fx import all as afx
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap

W, H = 1080, 1920
DURATION = 22  # seconds

# ---------- helpers ----------
def _load_font(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()

def make_line_img(text: str, size: int = 64, wrap: int = 22):
    """Render ONE line of caption to a transparent RGBA image."""
    font = _load_font(size)
    line = textwrap.fill(text.strip(), width=wrap)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # box
    bbox = d.multiline_textbbox((0, 0), line, font=font, spacing=8, align="center")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (W - tw) // 2
    y = (H - th) // 2 - 60
    d.rectangle((x - 20, y - 20, x + tw + 20, y + th + 20), fill=(0, 0, 0, 120))
    d.multiline_text((x, y), line, font=font, fill=(255, 255, 255, 235),
                     spacing=8, align="center")
    return np.array(img)

def watermark_clip(brand: str, dur: float):
    font = _load_font(44)
    img = Image.new("RGBA", (W, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bb = d.textbbox((0, 0), brand, font=font)
    x = (W - (bb[2] - bb[0])) // 2
    d.text((x, 40), brand, font=font, fill=(255, 255, 255, 210))
    return ImageClip(np.array(img)).set_duration(dur).set_position(("center", H - 140)).set_opacity(0.96)

def gradient_bg(duration=DURATION):
    colors = [(20,20,30), (35,20,60), (20,40,80), (15,15,35)]
    clips = [ColorClip(size=(W,H), color=c, duration=max(1, duration//len(colors) or 1)) for c in colors]
    return concatenate_videoclips(clips, method="compose")

def make_background(topic: str | None):
    """Try to fetch football b-roll; fall back to animated gradient."""
    try:
        from broll import fetch_broll
        p = fetch_broll(topic or "football", outfile="broll.mp4")
        if p and os.path.exists(p):
            clip = VideoFileClip(p).without_audio()
            scale = H / clip.h
            resized = clip.resize(scale)
            if resized.w >= W:
                x1 = int((resized.w - W) / 2)
                bg = resized.crop(x1=x1, y1=0, x2=x1 + W, y2=H)
            else:
                bg = resized.resize(width=W).crop(y1=0, y2=H)
            return bg.fx(vfx.colorx, 1.06)
    except Exception:
        pass
    return gradient_bg()

# ---------- main render ----------
def render_video(script: str, brand_name: str = "QuickShorts",
                 outfile: str = "out.mp4", topic: str | None = None,
                 voice_path: str | None = None):
    bg = make_background(topic)
    dur = min(DURATION, bg.duration)

    narration = None
    if voice_path and os.path.exists(voice_path):
        try:
            narration = (AudioFileClip(voice_path)
                         .fx(afx.audio_fadein, 0.25)
                         .fx(afx.audio_fadeout, 0.25))
            dur = min(dur, narration.duration)
        except Exception:
            narration = None

    bg = bg.subclip(0, dur)

    # --- animated captions: show ONE line at a time ---
    lines = [ln.strip() for ln in script.splitlines() if ln.strip()]
    if not lines:
        lines = ["Football fact"]
    per = dur / len(lines)

    overlay_clips = []
    for i, line in enumerate(lines):
        img = make_line_img(line)
        clip = (ImageClip(img)
                .set_start(i * per)
                .set_duration(per)
                .fadein(0.2)
                .fadeout(0.2)
                .set_position("center")
                .set_opacity(0.98))
        overlay_clips.append(clip)

    wm = watermark_clip(brand_name, dur)

    final = CompositeVideoClip([bg, wm] + overlay_clips, size=(W, H))
    if narration:
        final = final.set_audio(narration.set_duration(dur))

    final.write_videofile(
        outfile,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=2
    )
    return outfile
