import json, re, os, subprocess

schemes = json.load(open(r'C:\Users\aelha\Downloads\schemes_v3.json', encoding='utf-8'))

CODE_TO_ID = {
    'IP':'ip','PBCC':'pbcc','CGIS-1':'cgis-1','CIP-0':'cip-0','CIP-1':'cip-1','CIP-2':'cip-2',
    'CCIO-1':'ccio-1','CCIO-2':'ccio-2','CGIT':'cgit','CGT':'cgt',
    'CDT-1':'cdt-1','CDT-2':'cdt-2','CDTT-3':'cdtt-3',
    'CFF-1':'cff-1','CFF-2':'cff-2','CFF-3':'cff-3','CFF-4':'cff-4','CFF-5':'cff-5',
    'CLF-1':'clf-1','CIL':'cil',
    'MCI-1':'mci-1','MCI-2':'mci-2','MCI-3':'mci-3','MCI-4':'mci-4',
    'CAAP':'caap','CGA':'cga','CIME':'cime','CTC':'ctc','CLC':'clc',
}

BACKSLASH = chr(92)
APOSTROPHE = chr(39)

def js_str(s):
    s = s.replace(BACKSLASH, BACKSLASH + BACKSLASH)
    s = s.replace(APOSTROPHE, BACKSLASH + APOSTROPHE)
    s = s.replace('\n', ' ').replace('\r', ' ')
    return ' '.join(s.split())

def fmt_hours(h):
    h = str(h).strip()
    if not h or h.lower() in ('none', 'nan', ''): return 'TBD'
    if 'month' in h.lower(): return h
    if h.lower() == 'variable': return 'Variable'
    if '-' in h: return f'{h}h'
    try:
        n = float(h)
        return f'{int(n)}h' if n == int(n) else f'{n}h'
    except: return h

def fmt_fee(f):
    if f is None or str(f).strip() == '': return ('TBD', None)
    try:
        n = float(f)
        if n == 0: return ('Free', 0)
        return (f'${int(n):,}' if n == int(n) else f'${n:,.2f}', n)
    except: return (str(f), None)

def shorten_tagline(desc, max_len=120):
    if not desc: return ''
    first = desc.split('.')[0].strip()
    return first if len(first) <= max_len else first[:max_len].rsplit(' ', 1)[0] + '...'

p = r'C:\Users\aelha\Downloads\gimi-store.html'
s = open(p, encoding='utf-8').read()
updates = []

for sch in schemes:
    code = sch['code']
    pid = CODE_TO_ID.get(code)
    if not pid: continue

    pat = re.compile(r"mk\(\{ id:'" + re.escape(pid) + r"',.*?\}\)", re.DOTALL)
    m = pat.search(s)
    if not m: continue
    block = m.group(0)
    new_block = block

    new_title = js_str(sch['fullname'])
    new_tag   = js_str(shorten_tagline(sch['description']))
    new_desc  = js_str(sch['description'])
    new_dur   = js_str(fmt_hours(sch['hours']))
    pd, np    = fmt_fee(sch['fee'])
    pd_esc    = js_str(pd)

    new_block = re.sub(r"title:'[^']*(?:\\'[^']*)*'",
                       lambda mo: f"title:'{new_title}'", new_block, count=1)
    new_block = re.sub(r"tagline:'[^']*(?:\\'[^']*)*'",
                       lambda mo: f"tagline:'{new_tag}'", new_block, count=1)
    new_block = re.sub(r"description:'[^']*(?:\\'[^']*)*'",
                       lambda mo: f"description:'{new_desc}'", new_block, count=1)
    new_block = re.sub(r"duration:'[^']*'",
                       lambda mo: f"duration:'{new_dur}'", new_block, count=1)
    new_block = re.sub(r"priceDisplay:'[^']*'",
                       lambda mo: f"priceDisplay:'{pd_esc}'", new_block, count=1)
    if np is not None:
        new_block = re.sub(r"\bprice:\s*-?\d+(?:\.\d+)?",
                           lambda mo: f"price:{int(np) if np == int(np) else np}",
                           new_block, count=1)

    prereq = sch['prereq'].strip()
    if prereq and prereq.lower() not in ('none', 'nan', ''):
        pt = js_str(f'{prereq} required.')
        if "prereqs:" in new_block:
            new_block = re.sub(r"prereqs:'[^']*(?:\\'[^']*)*'",
                               lambda mo: f"prereqs:'{pt}'", new_block, count=1)
        else:
            new_block = re.sub(r"(\s+)description:",
                               lambda mo: mo.group(1) + f"prereqs:'{pt}'," + mo.group(1) + "description:",
                               new_block, count=1)

    if new_block != block:
        s = s.replace(block, new_block)
        updates.append(code)

open(p, 'w', encoding='utf-8').write(s)
print(f'Updated {len(updates)} products')

r = subprocess.run(
    ['node', '-e',
     "const fs=require('fs');"
     "const h=fs.readFileSync(String.raw`" + p + "`,'utf8');"
     "const m=h.match(/<script>([\\s\\S]*?)<\\/script>/);"
     "try{new Function(m[1]);console.log('JS OK')}catch(e){console.log('Err:',e.message)}"],
    capture_output=True, text=True)
print(r.stdout.strip())
if r.stderr: print('STDERR:', r.stderr.strip()[:200])
