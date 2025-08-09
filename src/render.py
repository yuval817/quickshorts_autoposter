from moviepy.editor import ImageClip, CompositeVideoClip, ColorClip, concatenate_videoclips
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap

W, H = 1080, 1920
DURATION = 22

def gradient_bg(duration=DURATION):
    colors = [(20,20,30), (35,20,60), (20,40,80), (15,15,35)]
    clips = [ColorClip(size=(W,H), color=c, duration=duration//len(colors) or 1) for c in colors]
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
        font = ImageFont.load_default()
        wm_font = ImageFont.load_default()

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

def render_video(script: str, brand_name: str = "QuickShorts", outfile: str = "out.mp4"):
    bg = gradient_bg()
    overlay_np = make_text_image(script, brand_name)
    overlay = ImageClip(overlay_np).set_duration(bg.duration)
    final = CompositeVideoClip([bg, overlay], size=(W,H))
    final.write_videofile(outfile, fps=30, codec="libx264", audio=False, preset="medium", threads=2)
    return outfile
