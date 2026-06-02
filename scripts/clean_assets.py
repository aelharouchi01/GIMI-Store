"""
clean_assets.py — reduce gimi-store-assets/ to ONLY the images the site uses.

The 'used' set is parsed directly from the store HTML (source of truth), so
nothing referenced can be deleted. Everything else under gimi-store-assets/
(unused root images, the books/ v50/ badges/ folders, and v2/image* raw
extraction leftovers) is removed. Empty folders are pruned.

Dry-run unless RUN=1 is passed as argv[1].
"""

import os, re, sys

BASE = os.path.dirname(os.path.dirname(__file__))
HTML = os.path.join(BASE, "index.html")
ASSETS = os.path.join(BASE, "gimi-store-assets")
RUN = len(sys.argv) > 1 and sys.argv[1] == "RUN"

html = open(HTML, encoding="utf-8").read()

# Every gimi-store-assets/... path referenced anywhere in the HTML
refs = re.findall(r"gimi-store-assets/([^'\"\)\s]+\.(?:png|jpg|jpeg|svg|webp|gif))", html, re.I)
used = set(p.replace("\\", "/") for p in refs)  # e.g. {"v2/cip-0.png", "2x.jpeg", "gimi-logo-white.png"}

print(f"Used images referenced by HTML: {len(used)}")

removed_files = 0
removed_bytes = 0
kept = 0

for root, dirs, files in os.walk(ASSETS):
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, ASSETS).replace("\\", "/")
        if rel in used:
            kept += 1
        else:
            removed_files += 1
            removed_bytes += os.path.getsize(full)
            if RUN:
                os.remove(full)

# prune empty dirs
pruned_dirs = []
if RUN:
    for root, dirs, files in os.walk(ASSETS, topdown=False):
        if root == ASSETS:
            continue
        if not os.listdir(root):
            os.rmdir(root)
            pruned_dirs.append(os.path.relpath(root, ASSETS))

mode = "REMOVED" if RUN else "WOULD REMOVE"
print(f"Kept: {kept}")
print(f"{mode}: {removed_files} files ({removed_bytes/1024/1024:.1f} MB)")
if pruned_dirs:
    print(f"Pruned empty folders: {', '.join(pruned_dirs)}")

# Sanity: every used file must still exist
missing = [u for u in used if not os.path.exists(os.path.join(ASSETS, u))]
if missing:
    print(f"\n[!] WARNING: {len(missing)} used files NOT found on disk: {missing}")
else:
    print("\n[OK] All used files present on disk.")
