from moviepy.editor import TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips
from moviepy.video.fx.all import resize
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import textwrap
import random

W, H = 1080, 1920
DURATION = 22

def gradient_bg(duration=DURATION):
    # Simple vertical gradient animation
    frames = []
    # We'll simulate gradient by crossfading color clips
    colors = [(20,20,30), (35,20,60), (20,40,80), (15,15,35)]
    clips = [ColorClip(size=(W,H), color=c, duration=duration/len(colors)) for c in colors]
    return concatenate_videoclips(clips, method="compose")

def make_caption_text(script:str):
    # Large readable text with line breaks
    lines = []
    for raw in script.splitlines():
        if not raw.strip(): 
            continue
        wrapped = textwrap.fill(raw.strip(), width=24)
        lines.append(wrapped)
    return "\n\n".join(lines)

def render_video(script:str, brand_name:str="QuickShorts", outfile:str="out.mp4"):
    bg = gradient_bg()
    caption = make_caption_text(script)

    txt = TextClip(caption, fontsize=70, font="Arial-Bold", size=(W-120,None), method="caption")
    txt = txt.set_position(("center","center")).set_duration(bg.duration)
    txt = txt.margin(left=60, right=60, top=60, bottom=60)

    # Watermark
    wm = TextClip(brand_name, fontsize=48, font="Arial-Bold")
    wm = wm.set_position(("center", H-120)).set_duration(bg.duration)

    final = CompositeVideoClip([bg, txt, wm], size=(W,H))
    final = final.set_duration(bg.duration)
    final.write_videofile(outfile, fps=30, codec="libx264", audio=False, preset="medium", threads=2)
    return outfile
