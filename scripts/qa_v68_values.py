"""Dump deck-vs-store values side by side to verify PASSes are real (not skips)."""
import re, json, io, os
BASE = os.path.dirname(os.path.dirname(__file__))
deck_txt = open(os.path.join(BASE,"data","v68_extracted.txt"),encoding="utf-8",errors="replace").read()
store = open(os.path.join(BASE,"index.html"),encoding="utf-8").read()

deck={}
for slide in re.split(r'<!-- Slide number: \d+ -->',deck_txt):
    m=re.search(r'^GIMI\s{2,}(.+?)\s{2,}(.+?)\s{2,}([A-Z][A-Z0-9\-]+)\s*$',slide,re.M)
    if not m: continue
    code=m.group(3).strip()
    cert=re.search(r'CERT PRICE\s*\n\s*(\$[\d,]+)',slide)
    train=re.search(r'CERT \+ TRAINING PRICE\s*\n\s*(\$[\d,]+)',slide)
    hours=re.search(r'TIME TO COMPLETE\s*\n\s*(.+)',slide) or re.search(r'\nTIME\s*\n\s*(.+)',slide)
    desc=re.search(r'DESCRIPTION\s*\n(.*?)(?=WHAT.S INCLUDED|SKILLS YOU|CAREER OUTCOMES|PROCESS|\Z)',slide,re.S)
    deck[code]={"cert":cert.group(1) if cert else None,"train":train.group(1) if train else None,
                "hours":hours.group(1).strip() if hours else None,
                "desc_len":len(re.sub(r'\s+',' ',desc.group(1)).strip()) if desc else 0}

prod=re.search(r'const PRODUCTS = \[(.*?)\n\];',store,re.S).group(1)
sp={}
for blk in re.findall(r'mk\(\{(.*?)\}\)',prod,re.S):
    cm=re.search(r"code:'([^']+)'",blk)
    if not cm: continue
    def g(k):
        mm=re.search(k+r":'([^']*)'",blk); return mm.group(1) if mm else None
    dm=re.search(r"description:'(.*?)'(?=,?\s*\n|\}\))",blk,re.S)
    sp[cm.group(1)]={"cert":g("certDisplay"),"train":g("trainDisplay"),"duration":g("duration"),
                     "desc_len":len(dm.group(1)) if dm else 0}

o=io.StringIO()
o.write(f"{'CODE':8} | {'DECK cert/train/hours':32} | {'STORE cert/train/dur':32} | descLen d/s\n")
o.write("-"*100+"\n")
skip_price=skip_hours=skip_desc=0
for c in sorted(set(deck)&set(sp)):
    d,s=deck[c],sp[c]
    dprice=f"{d['cert']}/{d['train']}/{d['hours']}"
    sprice=f"{s['cert']}/{s['train']}/{s['duration']}"
    o.write(f"{c:8} | {dprice:32} | {sprice:32} | {d['desc_len']}/{s['desc_len']}\n")
    if not d['cert'] and not d['train']: skip_price+=1
    if not d['hours']: skip_hours+=1
    if d['desc_len']==0: skip_desc+=1
o.write("-"*100+"\n")
o.write(f"Deck rows with NO price data (would skip price check): {skip_price}\n")
o.write(f"Deck rows with NO hours data (would skip hours check): {skip_hours}\n")
o.write(f"Deck rows with NO description (would skip desc check): {skip_desc}\n")
open(os.path.join(BASE,"data","qa_v68_values.txt"),"w",encoding="utf-8").write(o.getvalue())
print("written data/qa_v68_values.txt")
print(f"skips -> price:{skip_price} hours:{skip_hours} desc:{skip_desc}")
