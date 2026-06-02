"""Build labeled contact sheets of all logo deck images so each can be identified."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(BASE, "data", "logos_unpacked", "ppt", "media")

imgs = sorted(os.listdir(SRC), key=lambda n: int(''.join(c for c in n if c.isdigit())))
imgs = [i for i in imgs if i.lower().endswith(".png")]

CELL = 300
LABEL_H = 40
COLS = 5
rows = (len(imgs) + COLS - 1) // COLS

# White background so transparent logos are visible
sheet_w = COLS * CELL
sheet_h = rows * (CELL + LABEL_H)
sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
draw = ImageDraw.Draw(sheet)

try:
    font = ImageFont.truetype("arial.ttf", 22)
except Exception:
    font = ImageFont.load_default()

for idx, name in enumerate(imgs):
    col = idx % COLS
    row = idx // COLS
    x = col * CELL
    y = row * (CELL + LABEL_H)

    im = Image.open(os.path.join(SRC, name)).convert("RGBA")
    # paste on white
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    im = bg.convert("RGB")
    im.thumbnail((CELL - 10, CELL - 10))
    px = x + (CELL - im.width) // 2
    py = y + LABEL_H + (CELL - im.height) // 2
    sheet.paste(im, (px, py))
    draw.rectangle([x, y, x + CELL - 1, y + CELL + LABEL_H - 1], outline="black", width=1)
    draw.text((x + 6, y + 8), name, fill="black", font=font)

out = os.path.join(BASE, "data", "logo_sheet.png")
sheet.save(out)
print(f"Saved {out} ({len(imgs)} images)")
