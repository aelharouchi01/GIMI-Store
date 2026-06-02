import os
from PIL import Image, ImageChops

BASE = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(BASE, "data", "logos_unpacked", "ppt", "media")

imgs = sorted([i for i in os.listdir(SRC) if i.lower().endswith(".png")],
              key=lambda n: int(''.join(c for c in n if c.isdigit())))

for name in imgs:
    im = Image.open(os.path.join(SRC, name))
    mode = im.mode
    w, h = im.size
    has_alpha = mode in ("RGBA", "LA") or (mode == "P" and "transparency" in im.info)
    alpha_bbox = None
    if has_alpha:
        rgba = im.convert("RGBA")
        alpha = rgba.split()[-1]
        alpha_bbox = alpha.getbbox()  # bounding box of non-zero alpha
    print(f"{name:14s} {mode:5s} {w}x{h:<4} alpha={has_alpha} content_bbox={alpha_bbox}")
