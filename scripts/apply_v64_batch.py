import json, re, subprocess
BS=chr(92); SQ=chr(39); EMDASH=chr(0x2014); BULLET=chr(0x25CF)
HTML=r'C:\Users\aelha\Downloads\gimi-store.html'
html=open(HTML,encoding='utf-8').read()
inc=json.load(open('v64_includes.json',encoding='utf-8'))
def js(s): return s.replace(BS,BS+BS).replace(SQ,BS+SQ)
def block_span(pid):
    s=html.find("mk({ id:'"+pid+"',")
    if s<0: return None
    i=html.find('{',s); depth=1; j=i
    while depth>0:
        j+=1
        if html[j]=='{':depth+=1
        elif html[j]=='}':depth-=1
    return s,j+1
def clean_includes(code, items):
    out=[x.replace(BULLET,'').strip() for x in items if x.replace(BULLET,'').strip()]
    merged=[]
    for x in out:
        if merged and re.search(r':\s*\d+$', merged[-1]) and x[:1].isdigit():
            merged[-1]=merged[-1]+' x '+x
        else: merged.append(x)
    return merged

C2I={'IP':'ip','PBCC':'pbcc','CGIS-1':'cgis-1','CIP-0':'cip-0','CIP-1':'cip-1','CIP-2':'cip-2','CIP-MC':'cip-mc','CCIO-1':'ccio-1','CCIO-2':'ccio-2','CCIO-MC':'ccio-mc','CGIT':'cgit','CGT':'cgt','CDT-1':'cdt-1','CDT-2':'cdt-2','CDTT-3':'cdtt-3','CFF-1':'cff-1','CFF-2':'cff-2','CFF-3':'cff-3','CFF-4':'cff-4','CFF-5':'cff-5','CLF-1':'clf-1','CIL':'cil','MCI-1':'mci-1','MCI-2':'mci-2','MCI-3':'mci-3','MCI-4':'mci-4','CAAP':'caap','CGA':'cga','CIME':'cime','CTC':'ctc','CLC':'clc'}
n_inc=0
for code,pid in C2I.items():
    items=clean_includes(code, inc.get(code,[]))
    if not items: continue
    arr="["+",".join("'"+js(x)+"'" for x in items)+"]"
    span=block_span(pid); block=html[span[0]:span[1]]
    if 'includes:' in block:
        nb=re.sub(r"includes:\[[^\]]*\]","includes:"+arr,block,count=1)
    else:
        nb=re.sub(r"(\s+)description:",lambda m:m.group(1)+"includes:"+arr+","+m.group(1)+"description:",block,count=1)
    if nb!=block: html=html[:span[0]]+nb+html[span[1]:]; n_inc+=1
print('includes set:',n_inc)

# CIP-1 eligibility
elig=["Completion of GIMI's Level 1 in-house training","Completion of a Certified Training Provider's (CTP) authorized preparatory training","Reading of the GIMI Innovation Management Book of Knowledge (Level 1)","Holding an MBA from a recognized institution","Completion of other recognized innovation training programs"]
elig_arr="["+",".join("'"+js(x)+"'" for x in elig)+"]"
note="Completing a training program does not guarantee certification and confers no advantage in the examination process. The certification decision is based solely on examination performance."
span=block_span('cip-1'); block=html[span[0]:span[1]]
ins="eligibilityIntro:'Candidates must satisfy at least one of the following routes to certification:', eligibility:"+elig_arr+", eligNote:'"+js(note)+"',"
nb=re.sub(r"(\s+)description:",lambda m:m.group(1)+ins+m.group(1)+"description:",block,count=1)
html=html[:span[0]]+nb+html[span[1]:]
print('CIP-1 eligibility added')

# Platinum+ membership (insert after memb-plat's '}),')
span=block_span('memb-plat')
close_paren=html.find(')',span[1])
comma=html.find(',',close_paren)
ins_at=comma+1
platplus=("\n\n  mk({ id:'memb-plat-plus', track:'memb',\n"
 "      title:'Corporate Membership "+EMDASH+" Platinum +',\n"
 "      tagline:'GIMI"+BS+SQ+"s top enterprise tier for organisations scaling innovation at the largest scale.',\n"
 "      price:100000, priceDisplay:'$100,000', duration:'Annual', target:'Enterprises',\n"
 "      badge:'gimi-store-assets/v2/memb-plat.png',\n"
 "      includes:['10 free masterclass seats','1000 individual innovation potential assessments','1 free organisational assessment + action roadmap','1 free coaching session + 30% off future','10 free award entries + 2 ceremony tickets','5 yearly CoE reports + 1 committee seat','Both innovation platforms free + AKAIO software','Open Innovation Challenge included'],\n"
 "      description:'The Platinum + Corporate Membership is GIMI"+BS+SQ+"s top enterprise tier. It bundles 10 masterclass seats, 1000 individual assessments, a full organisational assessment with action roadmap, coaching, award entries, Centers of Excellence access, both innovation platforms with AKAIO software, and the Open Innovation Challenge.'}),")
html=html[:ins_at]+platplus+html[ins_at:]
print('Platinum+ added after memb-plat')

open(HTML,'w',encoding='utf-8').write(html)
r=subprocess.run(['node','-e',
 "const fs=require('fs');const h=fs.readFileSync(String.raw`"+HTML+"`,'utf8');"
 "const m=h.match(/<script>([" + BS+"s"+BS+"S]*?)<"+BS+"/script>/);"
 "try{new Function(m[1]);console.log('JS OK')}catch(e){console.log('Err:',e.message)}"],
 capture_output=True,text=True)
print(r.stdout.strip(), r.stderr.strip()[:200])
