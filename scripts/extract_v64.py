import os, re, json
d = r'C:\Users\aelha\AppData\Local\Temp\gimi_v64\ppt\slides'
SLIDE_CODE = {
 5:'CIP-0',6:'CIP-1',7:'CIP-2',8:'CIP-MC',9:'CCIO-1',10:'CCIO-2',11:'CCIO-MC',
 12:'CGIS-1',13:'CGIT',14:'CGT',16:'IP',17:'PBCC',18:'CDT-1',19:'CDT-2',20:'CDTT-3',
 21:'CAAP',22:'CGA',23:'CIME',24:'CTC',25:'CLC',27:'CFF-1',28:'CFF-2',29:'CFF-3',
 30:'CFF-4',31:'CFF-5',33:'CLF-1',34:'CIL',36:'MCI-1',37:'MCI-2',38:'MCI-3',39:'MCI-4'}

LABELS={'EXAM FORMAT','PASS','RECERT','CERTIFICATE','GIMI PRODUCT CATALOG','PROCESS & EXAMINATION',
 'CERT PRICE','CERT + TRAINING PRICE','TIME','TIME TO COMPLETE','FOR','DESCRIPTION'}
def is_label(r):
    u=r.upper()
    return (u in LABELS or u.startswith('WHAT') or u.startswith('SKILLS') or u.startswith('CAREER')
            or u.startswith('GIMI PRODUCT'))

def runs(n):
    return [t.strip() for t in re.findall(r'<a:t>([^<]*)</a:t>', open(os.path.join(d,f'slide{n}.xml'),encoding='utf-8').read())]

def val_after(rs, label, stop_at_label=True):
    for i,r in enumerate(rs):
        if r.upper()==label.upper():
            vals=[]
            for x in rs[i+1:]:
                if not x: continue
                if stop_at_label and is_label(x): break
                vals.append(x)
            return ' '.join(vals).strip()
    return None

def description(rs):
    out=[]; cap=False
    for r in rs:
        if r.upper()=='DESCRIPTION': cap=True; continue
        if cap:
            if r.upper().startswith('WHAT'): break
            if r: out.append(r)
    return ' '.join(' '.join(out).split())

out={}
for n,code in SLIDE_CODE.items():
    rs=runs(n)
    rec={
     'cert': val_after(rs,'CERT PRICE'),
     'train': val_after(rs,'CERT + TRAINING PRICE'),
     'time': val_after(rs,'TIME') or val_after(rs,'TIME TO COMPLETE'),
     'for': val_after(rs,'FOR'),
     'exam': val_after(rs,'EXAM FORMAT'),
     'pass': val_after(rs,'PASS'),
     'recert': val_after(rs,'RECERT'),
     'certificate': val_after(rs,'CERTIFICATE'),
     'desc': description(rs),
    }
    # normalize recert bullet
    if rec['recert']:
        rec['recert']=re.sub(r'\s+,',',',rec['recert'].replace(chr(0x25CF),',').replace(chr(0x2022),','))
        rec['recert']=' '.join(rec['recert'].split())
    out[code]=rec
json.dump(out, open('v64_certs.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{"CODE":8}{"CERT":>9}{"TRAIN":>11}{"TIME":>11}   desc_len')
for code in SLIDE_CODE.values():
    r=out[code]
    print(f'{code:8}{str(r["cert"]):>9}{str(r["train"]):>11}{str(r["time"]):>11}   {len(r["desc"])}')
