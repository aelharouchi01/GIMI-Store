import os, re, json
d = r'C:\Users\aelha\AppData\Local\Temp\gimi_v64\ppt\slides'
SLIDE_CODE = {5:'CIP-0',6:'CIP-1',7:'CIP-2',8:'CIP-MC',9:'CCIO-1',10:'CCIO-2',11:'CCIO-MC',
 12:'CGIS-1',13:'CGIT',14:'CGT',16:'IP',17:'PBCC',18:'CDT-1',19:'CDT-2',20:'CDTT-3',
 21:'CAAP',22:'CGA',23:'CIME',24:'CTC',25:'CLC',27:'CFF-1',28:'CFF-2',29:'CFF-3',
 30:'CFF-4',31:'CFF-5',33:'CLF-1',34:'CIL',36:'MCI-1',37:'MCI-2',38:'MCI-3',39:'MCI-4'}
def runs(n): return [t.strip() for t in re.findall(r'<a:t>([^<]*)</a:t>', open(os.path.join(d,f'slide{n}.xml'),encoding='utf-8').read())]
def included(n):
    rs=runs(n); out=[]; cap=False
    for r in rs:
        u=r.upper()
        if u.startswith('WHAT') and 'INCLUDED' in u: cap=True; continue
        if cap:
            if u.startswith('SKILLS') or u.startswith('CAREER') or u.startswith('PROCESS'): break
            if r and r!=chr(0x2022): out.append(r)
    # merge runs that are continuations (lines starting with bullet/●)
    merged=[]
    for x in out:
        if x.startswith(chr(0x25CF)) or x.startswith(chr(0x2022)):
            # continuation of previous
            if merged: merged[-1]=merged[-1]+' '+x.lstrip(chr(0x25CF)+chr(0x2022)+' ').strip()
            else: merged.append(x.lstrip(chr(0x25CF)+chr(0x2022)+' ').strip())
        else:
            merged.append(x)
    return [m.strip() for m in merged if m.strip()]
inc={}
for n,code in SLIDE_CODE.items():
    inc[code]=included(n)
json.dump(inc, open('v64_includes.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
for code in ['CIP-MC','CCIO-MC','IP','CGIS-1','CGT','CFF-4']:
    print(f'{code}:'); [print('   -',x) for x in inc[code]]; print()
