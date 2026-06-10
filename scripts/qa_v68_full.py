"""
qa_v68_full.py — full QA of the store (index.html) vs V68 deck across:
  1 Prices  2 Taxonomy  3 Codes  4 Descriptions  5 Hours
(Logos = dimension 6 are checked visually, separately.)

Writes a UTF-8 report to data/qa_v68_report.txt.
FF hours (CFF-1..5) are validated against data/duration_overrides.json
(authoritative, from the FF team email) rather than the deck's "Self-paced".
"""
import re, json, io, os

BASE = os.path.dirname(os.path.dirname(__file__))
deck_txt = open(os.path.join(BASE, "data", "v68_extracted.txt"), encoding="utf-8", errors="replace").read()
store = open(os.path.join(BASE, "index.html"), encoding="utf-8").read()
overrides = json.load(open(os.path.join(BASE, "data", "duration_overrides.json"), encoding="utf-8"))["overrides"]

out = io.StringIO()
def w(s=""): out.write(s + "\n")

# ---------- group/cluster mapping (deck -> store) ----------
GROUP2TRACK = {
    "Innovation Core": "icore", "Innovation Elective": "ielec",
    "Future Foresight": "ff", "Leadership Core": "lead", "Consulting Core": "cons",
}
CLUSTER2STORE = {
    "CIP series": "cip", "CIP Masterclass": "cip-mc", "CCIO series": "ccio",
    "CCIO Masterclass": "ccio-mc", "GIMI Impact": "impact",
    "Foresight series": "ff-series",
    # "Train the Trainer" is ambiguous (icore vs ff) -> resolved by group below
}

# ---------- parse the deck ----------
deck = {}
for slide in re.split(r'<!-- Slide number: \d+ -->', deck_txt):
    m = re.search(r'^GIMI\s{2,}(.+?)\s{2,}(.+?)\s{2,}([A-Z][A-Z0-9\-]+)\s*$', slide, re.M)
    if not m:
        continue
    group, cluster, code = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    lines = [l.strip() for l in slide.split('\n') if l.strip() and not l.strip().startswith('![')]
    # title = line after the breadcrumb line
    title = None
    for i, l in enumerate(lines):
        if l.endswith(code) and l.startswith('GIMI'):
            if i + 1 < len(lines):
                title = lines[i + 1]
            break
    cert = re.search(r'CERT PRICE\s*\n\s*(\$[\d,]+)', slide)
    train = re.search(r'CERT \+ TRAINING PRICE\s*\n\s*(\$[\d,]+)', slide)
    hours = re.search(r'TIME TO COMPLETE\s*\n\s*(.+)', slide) or re.search(r'\nTIME\s*\n\s*(.+)', slide)
    desc = re.search(r'DESCRIPTION\s*\n(.*?)(?=WHAT.S INCLUDED|SKILLS YOU|CAREER OUTCOMES|PROCESS|\Z)', slide, re.S)
    d_desc = None
    if desc:
        d_desc = re.sub(r'!\[.*?\]\(.*?\)', '', desc.group(1))
        d_desc = re.sub(r'\s+', ' ', d_desc).strip()
    deck[code] = {
        "group": group, "cluster": cluster, "title": title,
        "cert": cert.group(1) if cert else None,
        "train": train.group(1) if train else None,
        "hours": hours.group(1).strip() if hours else None,
        "desc": d_desc,
    }

# ---------- parse the store ----------
prod_block = re.search(r'const PRODUCTS = \[(.*?)\n\];', store, re.S).group(1)
store_p = {}
for blk in re.findall(r'mk\(\{(.*?)\}\)', prod_block, re.S):
    code_m = re.search(r"code:'([^']+)'", blk)
    if not code_m:
        continue
    code = code_m.group(1)
    def g(k):
        m = re.search(k + r":'([^']*)'", blk)
        return m.group(1) if m else None
    desc_m = re.search(r"description:'(.*?)'(?=,?\s*\n|\}\))", blk, re.S)
    store_p[code] = {
        "track": g("track"), "cluster": g("cluster"),
        "title": g("title"),
        "cert": g("certDisplay"), "train": g("trainDisplay"),
        "duration": g("duration"),
        "desc": desc_m.group(1).strip() if desc_m else None,
        "badge": g("badge"),
    }

def norm_price(p):
    if not p:
        return None
    p = str(p).replace(",", "").replace("*", "").strip()
    return p if p not in ("", "null", "None") else None

def norm_text(t):
    return re.sub(r'\s+', ' ', (t or "")).strip().lower()

# ---------- compare ----------
deck_codes = set(deck) ; store_codes = set(store_p)
PASS = "PASS"; FLAG = "FLAG"; NA = "n/a "
counts = {1: [0, 0], 2: [0, 0], 3: [0, 0], 4: [0, 0], 5: [0, 0]}  # [pass, flag]

w("=" * 78)
w("FULL QA — STORE vs V68 DECK  (1 Prices  2 Taxonomy  3 Codes  4 Desc  5 Hours)")
w("=" * 78)
w(f"Deck cert courses parsed: {len(deck_codes)}   Store products: {len(store_codes)}")

# Dimension 3 (codes) — presence both ways
only_deck = sorted(deck_codes - store_codes)
only_store = sorted(store_codes - deck_codes)
w("\n[3] CODES — coverage")
w(f"  In deck, missing from store: {only_deck or 'NONE'}")
w(f"  In store, not detailed in deck (books/tools/memberships expected): {len(only_store)} products")

w("\n" + "-" * 78)
w("PER-COURSE CHECK (deck-detailed courses)")
w("-" * 78)

for code in sorted(deck_codes & store_codes):
    d = deck[code]; s = store_p[code]
    row = []

    # 1 Prices
    dc, sc = norm_price(d["cert"]), norm_price(s["cert"])
    dt, st = norm_price(d["train"]), norm_price(s["train"])
    price_issues = []
    if dc and sc and dc != sc: price_issues.append(f"cert deck={dc} store={sc}")
    if dt and st and dt != st: price_issues.append(f"train deck={dt} store={st}")
    if dc and not sc: price_issues.append(f"cert deck={dc} store=MISSING")
    if dt and not st: price_issues.append(f"train deck={dt} store=MISSING")
    p1 = FLAG if price_issues else PASS
    counts[1][0 if p1 == PASS else 1] += 1

    # 2 Taxonomy
    exp_track = GROUP2TRACK.get(d["group"])
    tax_issues = []
    if exp_track and s["track"] != exp_track:
        tax_issues.append(f"track deck={d['group']}->{exp_track} store={s['track']}")
    exp_cluster = CLUSTER2STORE.get(d["cluster"])
    if d["cluster"] == "Train the Trainer":
        exp_cluster = "ff-train" if d["group"] == "Future Foresight" else "icore-train"
    if exp_cluster and s["cluster"] and s["cluster"] != exp_cluster:
        tax_issues.append(f"cluster deck={d['cluster']}->{exp_cluster} store={s['cluster']}")
    p2 = FLAG if tax_issues else PASS
    counts[2][0 if p2 == PASS else 1] += 1

    # 3 Code (join key matches by definition; mark PASS)
    p3 = PASS; counts[3][0] += 1

    # 4 Descriptions
    desc_issue = None
    if d["desc"] and s["desc"]:
        if norm_text(d["desc"])[:160] != norm_text(s["desc"])[:160]:
            desc_issue = True
    p4 = FLAG if desc_issue else PASS
    counts[4][0 if p4 == PASS else 1] += 1

    # 5 Hours
    hr_issue = None; hr_note = ""
    if code in overrides:
        want = overrides[code]["duration"]
        if s["duration"] != want:
            hr_issue = f"override={want} store={s['duration']}"
        hr_note = f"(override {want}; deck says '{d['hours']}')"
    else:
        if d["hours"] and s["duration"] and norm_text(d["hours"]) != norm_text(s["duration"]):
            hr_issue = f"deck={d['hours']} store={s['duration']}"
    p5 = FLAG if hr_issue else PASS
    counts[5][0 if p5 == PASS else 1] += 1

    w(f"\n{code:8s} {s['title'][:54]}")
    w(f"   1 Price {p1}  2 Tax {p2}  3 Code {p3}  4 Desc {p4}  5 Hours {p5} {hr_note}")
    for it in price_issues: w(f"       price> {it}")
    for it in tax_issues:   w(f"       taxon> {it}")
    if desc_issue:
        w(f"       desc > deck:  {d['desc'][:120]}...")
        w(f"       desc > store: {s['desc'][:120]}...")
    if hr_issue: w(f"       hours> {hr_issue}")

# ---------- summary ----------
w("\n" + "=" * 78)
w("SUMMARY (deck-detailed courses)")
names = {1: "Prices", 2: "Taxonomy", 3: "Codes", 4: "Descriptions", 5: "Hours"}
for k in range(1, 6):
    w(f"  {names[k]:13s}: {counts[k][0]} PASS / {counts[k][1]} FLAG")
w("=" * 78)

open(os.path.join(BASE, "data", "qa_v68_report.txt"), "w", encoding="utf-8").write(out.getvalue())
print("Report written to data/qa_v68_report.txt")
print(f"Deck courses: {len(deck_codes)} | Store: {len(store_codes)} | Compared: {len(deck_codes & store_codes)}")
for k in range(1, 6):
    print(f"  {names[k]}: {counts[k][0]} pass / {counts[k][1]} flag")
