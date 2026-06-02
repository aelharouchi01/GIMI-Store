"""
apply_logos_v2026.py  (v2 — verified mapping + crop-to-square)

Each logo in the 2026 logos deck was visually identified by reading its
badge text. Source images are 1920x1080 transparent frames with the circular
badge (~1080x1080) centred between transparent side-margins, which made them
render small and inconsistently. We crop each to its content bounding box and
pad to a centred square so every badge renders at a uniform size.

Products with NO logo in the 2026 deck (CIP-MC, CCIO-MC, PBCC) are restored
from the clean original badges in the Downloads backup.
"""

import os, shutil
from PIL import Image

BASE = os.path.dirname(os.path.dirname(__file__))
SRC  = os.path.join(BASE, "data", "logos_unpacked", "ppt", "media")
DST  = os.path.join(BASE, "gimi-store-assets", "v2")
DEPLOY_DST = os.path.join(BASE, "gimi-store-deploy", "gimi-store-assets", "v2")
BACKUP = r"C:\Users\aelha\Downloads\gimi-store-assets\v2"

# code -> deck image, VERIFIED by reading each badge's text/illustration
LOGO_MAP = {
    # Future Foresight
    "cff-1":  "image1.png",   # Foresight Professional L01
    "cff-2":  "image2.png",   # Foresight Leader L02
    "cff-3":  "image8.png",   # Foresight Officer L03
    "cff-4":  "image20.png",  # Trainer in Future Foresight L01
    "cff-5":  "image15.png",  # Trainer in Future Foresight L02
    # Leadership Core
    "clf-1":  "image4.png",   # Leader for the Future
    "cil":    "image18.png",  # Innovation Leader
    # Consulting Core
    "mci-1":  "image6.png",   # Mgmt Consulting Analyst L01
    "mci-2":  "image14.png",  # Mgmt Consulting Consultant L02
    "mci-3":  "image9.png",   # Mgmt Consulting Manager L03
    "mci-4":  "image5.png",   # Mgmt Consulting Leader L04
    # Innovation Elective
    "ip":     "image16.png",  # Innovation Primer
    "cdt-1":  "image19.png",  # Design Thinking L01
    "cdt-2":  "image7.png",   # Design Thinking L02
    "cdtt-3": "image3.png",   # Design Thinking Trainer
    "caap":   "image12.png",  # AI Agent Practitioner
    "cga":    "image17.png",  # GIMI Auditor
    "cime":   "image11.png",  # ISO Innovation Management Expert
    "ctc":    "image10.png",  # Technology Catalyst
    "clc":    "image21.png",  # Longevity Catalyst
    # Innovation Core
    "cip-0":  "image24.png",  # Innovation Professional - Innovation Champion (pawn)
    "cip-1":  "image26.png",  # Innovation Professional L01 (knight)
    "cip-2":  "image27.png",  # Innovation Professional L02 (bishop)
    "ccio-1": "image23.png",  # Chief Innovation Officer L03 (rook)
    "ccio-2": "image25.png",  # Chief Innovation Officer L04 (king)
    "cgis-1": "image22.png",  # GIMI Impact: Students
    "cgit":   "image28.png",  # GIMI Impact: Teachers
    "cgt":    "image29.png",  # GIMI Trainer
    # NOTE: image13 is a duplicate "Technology Catalyst" — unused.
    # NO deck logo for: cip-mc, ccio-mc, pbcc  -> restored from backup below.
}

# Products to restore from the clean Downloads backup (no logo in 2026 deck)
RESTORE = ["cip-mc", "ccio-mc", "pbcc"]


def square_crop(path):
    """Crop to alpha content bbox, then pad to a centred transparent square."""
    im = Image.open(path).convert("RGBA")
    bbox = im.split()[-1].getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    side = max(w, h)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - w) // 2, (side - h) // 2), im)
    return canvas


processed, restored, errors = [], [], []

for code, src_file in LOGO_MAP.items():
    src_path = os.path.join(SRC, src_file)
    if not os.path.exists(src_path):
        errors.append(f"MISSING SOURCE {src_file} for {code}")
        continue
    img = square_crop(src_path)
    for folder in (DST, DEPLOY_DST):
        if os.path.isdir(folder):
            img.save(os.path.join(folder, code + ".png"))
    processed.append(f"  {code:8s} <- {src_file}  ({img.size[0]}x{img.size[1]} square)")

for code in RESTORE:
    src = os.path.join(BACKUP, code + ".png")
    if not os.path.exists(src):
        errors.append(f"MISSING BACKUP for {code}")
        continue
    for folder in (DST, DEPLOY_DST):
        if os.path.isdir(folder):
            shutil.copy2(src, os.path.join(folder, code + ".png"))
    restored.append(f"  {code:8s} <- backup (no 2026 deck logo)")

print(f"Processed {len(processed)} deck logos, restored {len(restored)}, {len(errors)} errors\n")
print("DECK LOGOS (cropped to square):")
print("\n".join(processed))
print("\nRESTORED FROM BACKUP:")
print("\n".join(restored))
if errors:
    print("\nERRORS:")
    print("\n".join("  " + e for e in errors))
