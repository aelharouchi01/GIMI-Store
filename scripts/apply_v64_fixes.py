import json, re, subprocess
BS=chr(92); SQ=chr(39)
HTML=r'C:\Users\aelha\Downloads\gimi-store.html'
v64=json.load(open('v64_certs.json',encoding='utf-8'))
html=open(HTML,encoding='utf-8').read()

def js(s): return s.replace(BS,BS+BS).replace(SQ,BS+SQ)
def norm(s): return ' '.join(re.sub(r'\s+([.,])',r'\1',s).split())

def block_span(pid):
    s=html.find("mk({ id:'"+pid+"',"); i=html.find('{',s); depth=1; j=i
    while depth>0:
        j+=1
        if html[j]=='{':depth+=1
        elif html[j]=='}':depth-=1
    return s,j+1
def set_field(block,name,newval):
    key=name+":"+SQ; p=block.find(key)
    if p<0: return block,False
    k=p+len(key)
    while k<len(block):
        if block[k]==BS:k+=2;continue
        if block[k]==SQ:break
        k+=1
    return block[:p+len(key)]+newval+block[k:], True

# 1. Description updates (deck = source): IP, CLC, CIL
DESC_FIX = {'ip':'IP','clc':'CLC','cil':'CIL'}
# 2. Duration updates from deck
DUR_FIX = {'cff-1':'Self-paced','cff-2':'Self-paced','cff-3':'Self-paced','cff-4':'Self-paced',
           'cff-5':'Self-paced','ccio-mc':'4 weeks + 3-4 months mentoring'}
# (CCIO-2 intentionally NOT auto-changed -> flagged for decision)

changes=[]
def edit(pid, fn):
    global html
    s,e=block_span(pid); block=html[s:e]
    nb=fn(block)
    if nb!=block:
        html=html[:s]+nb+html[e:]; return True
    return False

for pid,code in DESC_FIX.items():
    newdesc=js(norm(v64[code]['desc']))
    def f(b,nd=newdesc): return set_field(b,'description',nd)[0]
    if edit(pid,f): changes.append(('DESC',code))

for pid,dur in DUR_FIX.items():
    def f(b,d=dur): return set_field(b,'duration',d)[0]
    if edit(pid,f): changes.append(('DUR',pid.upper(),dur))

open(HTML,'w',encoding='utf-8').write(html)
print('Applied:')
for c in changes: print('  ',c)

r=subprocess.run(['node','-e',
 "const fs=require('fs');const h=fs.readFileSync(String.raw`"+HTML+"`,'utf8');"
 "const m=h.match(/<script>([" + BS+"s"+BS+"S]*?)<"+BS+"/script>/);"
 "try{new Function(m[1]);console.log('JS OK')}catch(e){console.log('Err:',e.message)}"],
 capture_output=True,text=True)
print(r.stdout.strip(), r.stderr.strip()[:120])
