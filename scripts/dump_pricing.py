"""Dump current pricing fields for every product from index.html."""
import re, json

html = open("index.html", encoding="utf-8").read()
m = re.search(r'const PRODUCTS = \[(.*?)\n\];', html, re.DOTALL)
body = m.group(1)
blocks = re.findall(r'mk\(\{(.*?)\}\)', body, re.DOTALL)

def f(block, key):
    mm = re.search(key + r":\s*('([^']*)'|null|true|false|\d+)", block)
    if not mm: return None
    g = mm.group(1)
    if g in ('null','true','false'): return g
    return mm.group(2) if mm.group(2) is not None else g

rows = []
for b in blocks:
    rows.append({
        'code': f(b,'code') or '',
        'title': (f(b,'title') or '')[:42],
        'track': f(b,'track'),
        'cluster': f(b,'cluster'),
        'cert': f(b,'certDisplay'),
        'train': f(b,'trainDisplay'),
        'price': f(b,'priceDisplay'),
    })

# Print grouped by track
order = ['icore','ielec','ff','lead','cons','books','tools','memb']
names = {'icore':'INNOVATION CORE','ielec':'INNOVATION ELECTIVE','ff':'FUTURE FORESIGHT',
         'lead':'LEADERSHIP CORE','cons':'CONSULTING CORE','books':'BOOKS & GUIDES',
         'tools':'PROGRAMS & TOOLS','memb':'MEMBERSHIPS'}
for t in order:
    print(f"\n== {names[t]} ==")
    for r in rows:
        if r['track']==t:
            print(f"  {r['code'] or '(no code)':9} cert={str(r['cert']):8} train={str(r['train']):8} price={str(r['price']):16} | {r['title']}")
print(f"\nTotal products: {len(rows)}")
