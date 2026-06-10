"""Dump full deck vs store descriptions for codes where lengths diverged."""
import re, io, os
BASE = os.path.dirname(os.path.dirname(__file__))
deck_txt = open(os.path.join(BASE,"data","v68_extracted.txt"),encoding="utf-8",errors="replace").read()
store = open(os.path.join(BASE,"index.html"),encoding="utf-8").read()
TARGETS = ["CAAP","CCIO-1","CCIO-2","CCIO-MC","CGT"]

deck={}
for slide in re.split(r'<!-- Slide number: \d+ -->',deck_txt):
    m=re.search(r'^GIMI\s{2,}(.+?)\s{2,}(.+?)\s{2,}([A-Z][A-Z0-9\-]+)\s*$',slide,re.M)
    if not m: continue
    desc=re.search(r'DESCRIPTION\s*\n(.*?)(?=WHAT.S INCLUDED|SKILLS YOU|CAREER OUTCOMES|PROCESS|\Z)',slide,re.S)
    if desc:
        deck[m.group(3).strip()]=re.sub(r'\s+',' ',re.sub(r'!\[.*?\]\(.*?\)','',desc.group(1))).strip()

prod=re.search(r'const PRODUCTS = \[(.*?)\n\];',store,re.S).group(1)
sp={}
for blk in re.findall(r'mk\(\{(.*?)\}\)',prod,re.S):
    cm=re.search(r"code:'([^']+)'",blk)
    if not cm: continue
    dm=re.search(r"description:'(.*?)'(?=,?\s*\n|\}\))",blk,re.S)
    if dm: sp[cm.group(1)]=re.sub(r'\s+',' ',dm.group(1)).strip()

o=io.StringIO()
for c in TARGETS:
    o.write("="*90+f"\n{c}\n"+"="*90+"\n")
    o.write(f"DECK  ({len(deck.get(c,''))} chars):\n{deck.get(c,'<none>')}\n\n")
    o.write(f"STORE ({len(sp.get(c,''))} chars):\n{sp.get(c,'<none>')}\n\n")
open(os.path.join(BASE,"data","qa_desc_diff.txt"),"w",encoding="utf-8").write(o.getvalue())
print("written data/qa_desc_diff.txt")
