import re, json
BS=chr(92); SQ=chr(39)
html=open('gimi-store.html',encoding='utf-8').read()

def find_block(pid):
    s=html.find("mk({ id:'"+pid+"',")
    if s<0: return None
    i=html.find('{',s); depth=1; j=i
    while j<len(html) and depth>0:
        j+=1
        if html[j]=='{':depth+=1
        elif html[j]=='}':depth-=1
    return html[s:j+1]
def fval(block,name):
    key=name+":"+SQ; p=block.find(key)
    if p<0: return None
    k=p+len(key); out=[]
    while k<len(block):
        c=block[k]
        if c==BS: out.append(block[k+1]); k+=2; continue
        if c==SQ: break
        out.append(c); k+=1
    return ''.join(out)
def fdetail(block,key):
    # details:{ 'Exam Format':'...', ... }
    m=re.search(r"details:\{([^}]*)\}", block)
    if not m: return None
    d=m.group(1)
    mm=re.search(re.escape(key)+r"'\s*:\s*'((?:[^'"+BS+r"]|"+BS+r".)*)'", d)
    return None  # simplified; use direct scan
def detail_val(block,key):
    # find "key':' then scan
    needle = key + "':'"
    p = block.find(needle)
    if p<0:
        needle = key + "': '"
        p = block.find(needle)
        if p<0: return None
    k=p+len(needle); out=[]
    while k<len(block):
        c=block[k]
        if c==BS: out.append(block[k+1]); k+=2; continue
        if c==SQ: break
        out.append(c); k+=1
    return ''.join(out)

v64=json.load(open('v64_certs.json',encoding='utf-8'))
v64s=json.load(open('v64_storylines.json',encoding='utf-8'))
C2I={'IP':'ip','PBCC':'pbcc','CGIS-1':'cgis-1','CIP-0':'cip-0','CIP-1':'cip-1','CIP-2':'cip-2','CIP-MC':'cip-mc','CCIO-1':'ccio-1','CCIO-2':'ccio-2','CCIO-MC':'ccio-mc','CGIT':'cgit','CGT':'cgt','CDT-1':'cdt-1','CDT-2':'cdt-2','CDTT-3':'cdtt-3','CFF-1':'cff-1','CFF-2':'cff-2','CFF-3':'cff-3','CFF-4':'cff-4','CFF-5':'cff-5','CLF-1':'clf-1','CIL':'cil','MCI-1':'mci-1','MCI-2':'mci-2','MCI-3':'mci-3','MCI-4':'mci-4','CAAP':'caap','CGA':'cga','CIME':'cime','CTC':'ctc','CLC':'clc'}
order=['CIP-0','CIP-1','CIP-2','CIP-MC','CCIO-1','CCIO-2','CCIO-MC','CGIS-1','CGIT','CGT','IP','PBCC','CDT-1','CDT-2','CDTT-3','CAAP','CGA','CIME','CTC','CLC','CFF-1','CFF-2','CFF-3','CFF-4','CFF-5','CLF-1','CIL','MCI-1','MCI-2','MCI-3','MCI-4']
def ntx(s): return ' '.join((s or '').split())
def np(s): return None if s in (None,'') else str(s).replace('*','').strip()

price_iss=[]; desc_iss=[]; dur_iss=[]; card_iss=[]; story_iss=[]
for code in order:
    pid=C2I[code]; b=find_block(pid)
    sc=fval(b,'certDisplay'); st=fval(b,'trainDisplay'); sd=fval(b,'duration')
    sdesc=fval(b,'description'); stag=fval(b,'tagline')
    s_exam=detail_val(b,'Exam Format'); s_pass=detail_val(b,'Pass Threshold')
    s_rec=detail_val(b,'Recertification'); s_cert=detail_val(b,'Certificate')
    v=v64[code]
    # prices
    if np(sc)!=np(v['cert_clean']): price_iss.append((code,'CERT',sc,v['cert_clean']))
    if np(st)!=np(v['train_clean']): price_iss.append((code,'TRAIN',st,v['train_clean']))
    # description
    if ntx(sdesc)!=ntx(v['desc']):
        # find first diff
        a,bb=ntx(sdesc),ntx(v['desc']); dp=next((i for i,(x,y) in enumerate(zip(a,bb)) if x!=y),min(len(a),len(b)))
        desc_iss.append((code,len(a),len(bb)))
    # duration (masterclasses use deck time; courses: just flag if differs from v64 time)
    vtime = v['time_clean']
    if code in ('CIP-MC','CCIO-MC'):
        # store should match deck; CCIO-MC deck "4 weeks plus..." vs store "4 weeks"
        pass
    if ntx(sd)!=ntx(vtime):
        dur_iss.append((code,sd,vtime))
    # P&E cards
    for lbl,sv,vv in [('Exam',s_exam,v['exam']),('Pass',s_pass,v['pass']),('Recert',s_rec,v['recert']),('Cert',s_cert,v['certificate'])]:
        if ntx(sv)!=ntx(vv): card_iss.append((code,lbl,sv,vv))
    # storyline
    if ntx(stag)!=ntx(v64s.get(code)): story_iss.append((code,))

def sec(title,iss,fmt):
    print(f'\n=== {title} ({len(iss)} issues) ===')
    if not iss: print('  ALL MATCH'); return
    for x in iss: print('  '+fmt(x))

sec('1. PRICING (store vs V64)', price_iss, lambda x:f'[{x[0]:7}] {x[1]:5} store={x[2]!r} V64={x[3]!r}')
sec('2. DESCRIPTIONS (store vs V64)', desc_iss, lambda x:f'[{x[0]:7}] store_len={x[1]} V64_len={x[2]}')
sec('3. DURATION (store vs V64 TIME)', dur_iss, lambda x:f'[{x[0]:7}] store={x[1]!r} V64={x[2]!r}')
sec('4a. PROCESS&EXAM CARDS (store vs V64)', card_iss, lambda x:f'[{x[0]:7}] {x[1]:5} store={x[2]!r} V64={x[3]!r}')
sec('4b. STORYLINE (store vs V64)', story_iss, lambda x:f'[{x[0]:7}] differs')
