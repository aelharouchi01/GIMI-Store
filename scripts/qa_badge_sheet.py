"""High-res labeled sheet of specific v2 badges for visual QA."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
BASE = os.path.dirname(os.path.dirname(__file__))
V2 = os.path.join(BASE, "gimi-store-assets", "v2")
codes = sys.argv[1].split(",")
CELL = 360; LABEL = 46; COLS = 4
rows = (len(codes) + COLS - 1) // COLS
sheet = Image.new("RGB", (COLS*CELL, rows*(CELL+LABEL)), "white")
draw = ImageDraw.Draw(sheet)
try: font = ImageFont.truetype("arialbd.ttf", 30)
except Exception: font = ImageFont.load_default()
for i, c in enumerate(codes):
    x = (i % COLS)*CELL; y = (i // COLS)*(CELL+LABEL)
    p = os.path.join(V2, c+".png")
    im = Image.open(p).convert("RGBA"); bg = Image.new("RGBA", im.size, "white"); bg.alpha_composite(im)
    im = bg.convert("RGB"); im.thumbnail((CELL-12, CELL-12))
    sheet.paste(im, (x+(CELL-im.width)//2, y+(CELL-im.height)//2))
    draw.text((x+8, y+CELL+6), c, fill="black", font=font)
    draw.rectangle([x, y, x+CELL-1, y+CELL+LABEL-1], outline="#999")
out = os.path.join(BASE, "data", "qa_badges.png")
sheet.save(out); print(out)
