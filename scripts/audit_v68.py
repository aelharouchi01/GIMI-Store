"""
audit_v68.py — compare gimi-store.html against V68 deck extracted text.
Outputs a report of: product list differences, price mismatches, description mismatches.
"""

import re, json, sys

# ── 1. Parse the extracted V68 text ──────────────────────────────────────────

V68_TEXT = open("data/v68_extracted.txt", encoding="utf-8", errors="replace").read()

# Split into per-slide chunks
slides = re.split(r'<!-- Slide number: \d+ -->', V68_TEXT)

# Parse each slide that has a product code in the breadcrumb (e.g. "CIP-0", "CCIO-MC")
# Pattern: "GIMI      <category>      <series>      <CODE>" in the first ~5 lines of the slide
product_re = re.compile(
    r'GIMI\s+\S.*?\s+(\b[A-Z][A-Z0-9\-]+\b)\s*\n',
    re.MULTILINE
)

# More targeted: look for the code in the slide header line
# e.g. "GIMI      Innovation Core      CIP series      CIP-0"
breadcrumb_re = re.compile(
    r'^GIMI\s{2,}.+\s{2,}([A-Z][A-Z0-9\-]+)\s*$',
    re.MULTILINE
)

KNOWN_SKIPS = {'GIMI', 'PDF', 'ISO', 'IPA', 'OIA', 'AI', 'SME', 'SCDP', 'MCQ', 'CPE', 'TBD', 'FAQ'}

deck_products = {}  # code -> {title, cert_price, train_price, description}

for slide_text in slides:
    # Try to find breadcrumb
    m = breadcrumb_re.search(slide_text)
    if not m:
        continue
    code = m.group(1).strip()
    if code in KNOWN_SKIPS or len(code) < 3:
        continue

    # Extract title (first non-empty line after the breadcrumb line that looks like a title)
    lines = [l.strip() for l in slide_text.split('\n') if l.strip()]

    # Find title: typically the first "sentence" line after the breadcrumb header
    title = None
    desc = None
    cert_price = None
    train_price = None

    breadcrumb_idx = None
    for i, line in enumerate(lines):
        if code in line and 'GIMI' in line:
            breadcrumb_idx = i
            break

    if breadcrumb_idx is not None and breadcrumb_idx + 1 < len(lines):
        title = lines[breadcrumb_idx + 1]

    # Extract prices: "CERT PRICE\n$NNN" and "CERT + TRAINING PRICE\n$NNN"
    cert_m = re.search(r'CERT PRICE\s*\n?\s*(\$[\d,]+)', slide_text)
    train_m = re.search(r'CERT \+ TRAINING PRICE\s*\n?\s*(\$[\d,]+)', slide_text)
    if cert_m:
        cert_price = cert_m.group(1)
    if train_m:
        train_price = train_m.group(1)

    # Extract description: text between "DESCRIPTION" and "WHAT'S INCLUDED" (or next section)
    desc_m = re.search(r'DESCRIPTION\s*\n(.*?)(?=WHAT.S INCLUDED|SKILLS YOU|CAREER OUTCOMES|PROCESS|$)',
                       slide_text, re.DOTALL)
    if desc_m:
        raw = desc_m.group(1).strip()
        # Remove image references
        raw = re.sub(r'!\[.*?\]\(.*?\)', '', raw)
        raw = re.sub(r'\s+', ' ', raw).strip()
        desc = raw if raw else None

    deck_products[code] = {
        'title': title,
        'cert_price': cert_price,
        'train_price': train_price,
        'description': desc,
    }

# ── 2. Parse the store HTML ───────────────────────────────────────────────────

store_html = open("index.html", encoding="utf-8").read()

# Extract all mk({...}) blocks
# Find the PRODUCTS array
products_section_m = re.search(r'const PRODUCTS = \[(.*?)\];', store_html, re.DOTALL)
if not products_section_m:
    print("ERROR: Could not find PRODUCTS array in store HTML")
    sys.exit(1)

products_raw = products_section_m.group(1)

store_products = {}  # code -> {title, cert_price, train_price, description}

# Extract each mk({...}) block
mk_blocks = re.findall(r'mk\(\{(.*?)\}\)', products_raw, re.DOTALL)

for block in mk_blocks:
    code_m = re.search(r"code:'([^']+)'", block)
    title_m = re.search(r"title:'([^']+)'", block)
    cert_m = re.search(r"certDisplay:'([^']*)'", block)
    train_m = re.search(r"trainDisplay:'([^']*)'", block)
    desc_m = re.search(r"description:'(.*?)'(?=[,\n])", block, re.DOTALL)

    if not code_m:
        continue

    code = code_m.group(1)

    cert_display = cert_m.group(1) if cert_m else None
    train_display = train_m.group(1) if train_m else None

    # Normalize prices: strip $ and comma for comparison
    def norm_price(s):
        if not s:
            return None
        s = s.strip()
        if not s or s in ('null', ''):
            return None
        return s

    store_products[code] = {
        'title': title_m.group(1) if title_m else None,
        'cert_price': norm_price(cert_display),
        'train_price': norm_price(train_display),
        'description': desc_m.group(1).strip() if desc_m else None,
    }

# ── 3. Compare ────────────────────────────────────────────────────────────────

print("=" * 70)
print("GIMI STORE vs V68 AUDIT REPORT")
print("=" * 70)

deck_codes = set(deck_products.keys())
store_codes = set(store_products.keys())

print(f"\nV68 deck products found: {len(deck_codes)}")
print(f"Store products with codes: {len(store_codes)}")

# In deck but not store
in_deck_not_store = deck_codes - store_codes
if in_deck_not_store:
    print(f"\n[!] IN V68 DECK BUT NOT IN STORE ({len(in_deck_not_store)}):")
    for c in sorted(in_deck_not_store):
        print(f"    {c}: {deck_products[c]['title']}")
else:
    print("\n[OK] All V68 deck codes are present in the store.")

# In store but not deck
in_store_not_deck = store_codes - deck_codes
if in_store_not_deck:
    print(f"\n[!] IN STORE BUT NOT IN V68 DECK ({len(in_store_not_deck)}):")
    for c in sorted(in_store_not_deck):
        print(f"    {c}: {store_products[c]['title']}")
else:
    print("[OK] All store codes are present in the V68 deck.")

# Price comparison for products in both
print("\n" + "-" * 70)
print("PRICE COMPARISON (products present in both):")
price_mismatches = []
for code in sorted(deck_codes & store_codes):
    d = deck_products[code]
    s = store_products[code]

    # Compare cert price
    d_cert = d['cert_price']
    s_cert = s['cert_price']
    d_train = d['train_price']
    s_train = s['train_price']

    issues = []

    # Normalize for comparison
    def normalize(p):
        if p is None:
            return None
        p = str(p).replace(',', '').strip()
        if p in ('null', '', 'None'):
            return None
        return p

    dc = normalize(d_cert)
    sc = normalize(s_cert)
    dt = normalize(d_train)
    st = normalize(s_train)

    if dc and sc and dc != sc:
        issues.append(f"CERT: deck={dc} store={sc}")
    if dt and st and dt != st:
        issues.append(f"TRAIN: deck={dt} store={st}")
    if dc and not sc:
        issues.append(f"CERT: deck has {dc}, store is missing/null")
    if dt and not st:
        issues.append(f"TRAIN: deck has {dt}, store is missing/null")

    if issues:
        price_mismatches.append((code, issues))

if price_mismatches:
    print(f"  {len(price_mismatches)} price mismatch(es):")
    for code, issues in price_mismatches:
        print(f"  [{code}] {store_products[code]['title']}")
        for iss in issues:
            print(f"        -> {iss}")
else:
    print("  [OK] All prices match between store and deck.")

# Description comparison
print("\n" + "-" * 70)
print("DESCRIPTION COMPARISON (spot-check key products):")
desc_mismatches = []
for code in sorted(deck_codes & store_codes):
    d = deck_products[code]
    s = store_products[code]

    d_desc = (d['description'] or '').strip()
    s_desc = (s['description'] or '').strip()

    if not d_desc or not s_desc:
        continue

    # Normalize whitespace
    d_norm = re.sub(r'\s+', ' ', d_desc).lower()
    s_norm = re.sub(r'\s+', ' ', s_desc).lower()

    # Check first 120 chars (opening sentence)
    d_start = d_norm[:120]
    s_start = s_norm[:120]

    if d_start != s_start:
        desc_mismatches.append((code, d_desc[:200], s_desc[:200]))

if desc_mismatches:
    print(f"  {len(desc_mismatches)} description mismatch(es) found:")
    for code, d_desc, s_desc in desc_mismatches:
        print(f"\n  [{code}]")
        print(f"    DECK:  {d_desc[:150]}...")
        print(f"    STORE: {s_desc[:150]}...")
else:
    print("  [OK] All descriptions match (opening sentences align).")

# ── 4. Save structured deck data ─────────────────────────────────────────────
with open("data/v68_products.json", "w", encoding="utf-8") as f:
    json.dump(deck_products, f, indent=2, ensure_ascii=False)
print(f"\nDeck product data saved to data/v68_products.json")
print("=" * 70)
