import re, json
html = open('gimi-store.html', encoding='utf-8').read()
BS = chr(92); SQ = chr(39)

def parse_blocks(s):
    res=[]; i=0
    while True:
        idx=s.find('mk({', i)
        if idx<0: break
        depth=1; j=idx+3
        while j<len(s) and depth>0:
            j+=1
            if s[j]=='{': depth+=1
            elif s[j]=='}': depth-=1
        block=s[idx+3:j+1]
        res.append(block[block.find('{'):block.rfind('}')+1])
        i=s.find(')', j)+1
    return res

def field(b, name):
    key = name + ":" + SQ
    pos = b.find(key)
    if pos < 0: return None
    k = pos + len(key); out=[]
    while k < len(b):
        c = b[k]
        if c == BS: out.append(b[k+1]); k += 2; continue
        if c == SQ: break
        out.append(c); k += 1
    return ''.join(out)

m = re.search(r'const PRODUCTS = \[([\s\S]*?)\n\];', html)
blocks = parse_blocks(m.group(1))
# Map by id
ID_TO_CODE = {
 'ip':'IP','pbcc':'PBCC','cgis-1':'CGIS-1','cip-0':'CIP-0','cip-1':'CIP-1','cip-2':'CIP-2',
 'cip-mc':'CIP-MC','ccio-1':'CCIO-1','ccio-2':'CCIO-2','ccio-mc':'CCIO-MC','cgit':'CGIT','cgt':'CGT',
 'cdt-1':'CDT-1','cdt-2':'CDT-2','cdtt-3':'CDTT-3','cff-1':'CFF-1','cff-2':'CFF-2','cff-3':'CFF-3',
 'cff-4':'CFF-4','cff-5':'CFF-5','clf-1':'CLF-1','cil':'CIL','mci-1':'MCI-1','mci-2':'MCI-2',
 'mci-3':'MCI-3','mci-4':'MCI-4','caap':'CAAP','cga':'CGA','cime':'CIME','ctc':'CTC','clc':'CLC',
}
store = {}
for b in blocks:
    pid = field(b,'id')
    if pid not in ID_TO_CODE: continue
    code = ID_TO_CODE[pid]
    store[code] = {
        'has_code': field(b,'code') is not None,
        'cert': field(b,'certDisplay'),
        'train': field(b,'trainDisplay'),
        'duration': field(b,'duration'),
        'desc': field(b,'description') or ''
    }

deck = json.load(open('deck_prices.json', encoding='utf-8'))
crm  = json.load(open('crm_v3_2.json', encoding='utf-8'))

def npr(s):
    if s is None: return None
    return str(s).replace('*','').strip()
def ntx(s): return ' '.join((s or '').split())

DECK_DESC = {'CIP-MC','CCIO-MC'}
order = ['CIP-0','CIP-1','CIP-2','CIP-MC','CCIO-1','CCIO-2','CCIO-MC','CGIS-1','CGIT','CGT',
         'IP','PBCC','CDT-1','CDT-2','CDTT-3','CAAP','CGA','CIME','CTC','CLC',
         'CFF-1','CFF-2','CFF-3','CFF-4','CFF-5','CLF-1','CIL','MCI-1','MCI-2','MCI-3','MCI-4']

price_issues=[]; desc_issues=[]; missing=[]
for code in order:
    s = store.get(code)
    if not s: missing.append(code); continue
    dk = deck.get(code, {})
    sc, dc = npr(s['cert']), npr(dk.get('cert'))
    st, dt = npr(s['train']), npr(dk.get('train'))
    if sc != dc: price_issues.append((code,'CERT',sc,dc))
    if st != dt: price_issues.append((code,'TRAIN',st,dt))
    sd = ntx(s['desc'])
    if code in DECK_DESC:
        src, lbl = ntx(dk.get('desc')), 'DECK'
    else:
        src, lbl = ntx(crm.get(code,{}).get('description')), 'SHEET'
    if sd != src:
        # find first diff
        diffpos=None
        for i,(a,b2) in enumerate(zip(sd,src)):
            if a!=b2: diffpos=i; break
        desc_issues.append((code,lbl,len(sd),len(src),diffpos,
                            sd[max(0,(diffpos or 0)-20):(diffpos or 0)+20] if diffpos is not None else '',
                            src[max(0,(diffpos or 0)-20):(diffpos or 0)+20] if diffpos is not None else ''))

print('='*70)
print('QA RESULTS  ('+str(len(store))+' coded products checked)')
print('='*70)
print('\n--- 1. PRICING (store vs DECK) ---')
if not price_issues: print('  ALL PRICES MATCH')
else:
    for code,kind,sv,dv in price_issues:
        print(f'  MISMATCH [{code:7}] {kind:6} store={sv!r:12} deck={dv!r}')
print('\n--- 2/3. DESCRIPTIONS (certs vs SHEET, CIP-MC/CCIO-MC vs DECK) ---')
if not desc_issues: print('  ALL DESCRIPTIONS MATCH')
else:
    for code,lbl,sl,srl,dp,sx,sr in desc_issues:
        print(f'  MISMATCH [{code:7}] vs {lbl}: store_len={sl} src_len={srl} firstdiff@{dp}')
        if dp is not None:
            print(f'       store: ...{sx}...')
            print(f'       src  : ...{sr}...')
if missing: print('\n  PRODUCTS NOT FOUND:', missing)

# Also report which masterclasses lack a code chip
print('\n--- Note: code-chip presence ---')
for code in ['CIP-MC','CCIO-MC']:
    if code in store:
        print(f'  {code}: code chip {"PRESENT" if store[code]["has_code"] else "MISSING (no code field)"}')
